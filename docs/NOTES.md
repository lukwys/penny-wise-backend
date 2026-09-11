# Notes

Things that were not obvious the first time. Written down so I don't have to
re-derive them.

## Format

Newest entry on top. One entry per concept.

- **Heading** — phrase it as the *question you were stuck on*, not the name of
  the answer. Months later you search for the problem, not for the term you
  didn't know yet.
- **Problem** — what actually broke, or what didn't make sense. One or two
  sentences.
- **Why** — the mechanism. This is the part with the value. If it takes more
  than three sentences, the understanding isn't there yet.
- **Code** — a `file:line` anchor. A note with nothing to point at drifts into
  trivia.

Write it in your own words at the moment of confusion — not at the end of the
day, when you no longer remember which part was surprising.

---

## Does declaring the same dependency twice call it twice?

_TODO — dependency caching within a single request._

## Why `Annotated[X, Depends(...)]` instead of `x: X = Depends(...)`?

**Problem:** The SQLModel docs write dependencies as `session: Session =
Depends(get_session)`, and every single signature around them carries a bare `*`
as its first parameter. Two competing styles, and no explanation of the `*`.

**Why:** `= Depends(...)` hides the marker in the *default value*, so the
parameter claims a default it doesn't really have — call the function directly
(in a test, say) and you get a `Depends` object instead of a session. It also
drags in a Python rule: a parameter without a default may not follow one that
has a default. So the moment one parameter uses `= Depends(...)`, everything
after it needs a default too. The bare `*` sidesteps that by making all
parameters keyword-only, which lifts the ordering rule entirely. That's all the
`*` is — a workaround, not an idea.

`Annotated` puts the marker in the *type* instead. The parameter keeps no
default, so the ordering rule never applies, the `*` is unnecessary, and the
function stays an ordinary callable. It also has a name, which a default value
can't: `SessionDep = Annotated[Session, Depends(get_session)]` is declared once
and imported everywhere. Same syntax covers `Query`, `Header`, `Form` — one
mechanism instead of two conventions in one codebase.

**Code:** `app/database.py:20`

## Why does the DB session have to outlive the endpoint?

**Problem:** `create_expense` did its work inside `with Session(engine)` and
returned the new object after `commit()`. Returning it from outside the block
blew up with `DetachedInstanceError`; keeping the `return` inside the block
worked, which felt like an accident.

**Why:** SQLAlchemy expires every attribute on `commit()` — the object keeps its
identity but its values are marked stale, to be re-read on next access. Closing
the session also detaches it. So a detached + expired object has values it must
reload and no session to reload them through. Serialization by `response_model`
happens *after* the endpoint returns, so with a manual `with` block the session
is already gone by the time FastAPI touches the object.

A dependency with `yield` fixes this properly rather than by indentation: FastAPI
suspends the generator, runs the endpoint, serializes the response, and only then
resumes it to close the session. The session's lifetime becomes the *request*,
not the block. The `yield` must sit inside a `with` (or a `try`/`finally`) —
FastAPI throws endpoint exceptions back in at the `yield`, so a bare one would
skip the cleanup and leak connections from the pool.

**Code:** `app/database.py:16`
