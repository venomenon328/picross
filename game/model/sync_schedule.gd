extends RefCounted
## Seconds on a monotonic clock. Cell/view writes never arm a network request.
var clock := Callable(Time,"get_ticks_msec")
var due := INF
var retry_at := 0.0
var retry_floor := 0.0
var failures := 0
var active_since := INF
var auth_paused := false

func now() -> float: return float(clock.call()) / 1000.0

func enter() -> void: active_since = now()
func leave() -> void:
	active_since = INF
	collect()

func collect() -> void: due = minf(due, now()+2.0)

func connected() -> void:
	retry_at = minf(retry_at,maxf(now(),retry_floor))
	due = minf(due, now())

func transient(retry_after: int) -> void:
	failures = mini(failures+1,5)
	retry_floor = now()+maxi(30,retry_after)
	retry_at = maxf(retry_floor,now()+[30,60,120,240,300][failures-1])
	due = retry_at

func success() -> void:
	failures = 0
	retry_at = 0
	retry_floor = 0

func ready() -> bool:
	var stamp := now()
	if stamp >= active_since+600:
		active_since = stamp
		due = minf(due,stamp)
	return not auth_paused and stamp >= due and stamp >= retry_at
