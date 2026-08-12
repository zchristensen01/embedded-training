# fsm — variants

v1  Explicit `switch` on state, then on event. Verbose on purpose — this is the version you
    can read aloud to someone.
v2  Table-driven. A `const transition_t table[ST_COUNT][EV_COUNT]` where each cell holds
    `{next_state, action_fn}`, and `fsm_handle` becomes four lines. The table is the grid you
    drew on paper.
v3  Entry and exit actions, plus a timeout on `ST_HOMING` that faults if the limit switch
    never arrives. This is where `ticks_in_state` finally earns its place.
v4  Guarded transitions: a cell fires only if its predicate returns true, otherwise the event
    is ignored and counted. Decide whether a rejected event is an error or routine.
v5  No function pointers. Same table, but each cell holds an action *enum* dispatched through
    one `switch`. Compare code size and argue for one over the other.
v6  Hierarchical: a `FAULT` superstate that any state can enter, which remembers where it came
    from and can return there on a clear event.
v7  Event queue. `fsm_post(ev)` enqueues and `fsm_run()` drains, so an action can post an event
    without recursing into `fsm_handle`. State the queue depth and what happens when it fills.
