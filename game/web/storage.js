/* The only persistence backend is Godot's IDBFS /userfs mount. */
class PicrossStorage {
  constructor(label, retry) {
    this.label = label;
    this.retry = retry;
    this.ready = false;
    this.pending = false;
    this.error = '';
    this.localErrors = {};
    this.syncError = '';
    this.generation = 0;
    this.saved = 0;
    this.running = false;
    this.viewPending = false;
    retry.onclick = () => { if (window.picrossLifecycle) window.picrossLifecycle(); this.changed(); };
  }
  attach(fs, godotFS, idbfs) {
    if (!godotFS.is_persistent()) return false;
    this.fs = fs;
    // The pinned IDBFS glue does not catch transaction-construction errors in
    // reconcile's asynchronous caller. Return them through the same callback.
    const reconcile = idbfs.reconcile.bind(idbfs);
    idbfs.reconcile = (source, destination, callback) => {
      try { reconcile(source, destination, callback); }
      catch (error) { callback(error); }
    };
    // Serialize explicit and engine-triggered syncs, retaining their real callbacks.
    const original = fs.syncfs.bind(fs);
    let tail = Promise.resolve();
    fs.syncfs = (populate, callback) => {
      tail = tail.then(() => new Promise(resolve => {
        try { original(populate, error => { try { callback(error); } finally { resolve(); } }); }
        catch (error) { try { callback(error); } finally { resolve(); } }
      }));
    };
    this.ready = true;
    this.changed(); // A real transaction, not merely the capability check.
    return true;
  }
  viewChanged() { this.viewPending = true; this.pending = true; this.render(); }
  finished(slot, error) {
    if (error) this.localErrors[slot] = error;
    else delete this.localErrors[slot];
    this.changed();
  }
  changed() {
    this.generation++;
    this.viewPending = false;
    this.pending = true;
    this.render();
    // Run after the synchronous Godot file transaction has finished.
    queueMicrotask(() => this.sync());
  }
  sync() {
    if (!this.ready || this.running) return;
    this.running = true;
    const generation = this.generation;
    this.fs.syncfs(false, error => {
      this.running = false;
      if (error) {
        this.syncError = 'Browserspeicher fehlgeschlagen. Nicht schließen; Speichern erneut versuchen.';
        this.pending = true;
      } else {
        this.saved = generation;
        this.syncError = '';
        this.pending = this.saved !== this.generation || this.viewPending;
      }
      this.render();
      if (!error && this.saved !== this.generation) this.sync();
    });
  }
  render() {
    this.error = this.syncError || Object.values(this.localErrors)[0] || '';
    this.label.textContent = this.error || (this.pending ? 'Speichern läuft …' : 'Im Browser gespeichert');
    this.retry.hidden = !this.error;
  }
}
