---
name: silent-failure-hunter
description: Code review focused on detecting silent failures and error handling gaps. Targets empty exception handlers, insufficient logging, risky default behaviors, broken error chains, and absent safeguards. Zero tolerance for swallowed errors.
version: 1.0.0
license: Unlicense
category: integrity
keywords:
  - silent-failure
  - error-handling
  - swallowed-errors
  - empty-catch
  - missing-validation
  - reliability
  - code-review
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(grep:*)
  - Bash(rg:*)
compatibility:
  claude-code: ">=2.1"
---

# Silent Failure Hunter

> The bugs you don't see in the logs are the ones that lose you the most users.

## Why this skill exists

A silent failure is an error the system catches without the operator finding out. The most common form: a `try` block that catches every exception and continues. The code looks robust; the failure mode is invisible. This skill walks code with **zero tolerance** for that pattern.

## When this skill activates

- During code review of any new feature.
- During post-mortem of any production incident.
- Before promoting code from a review branch to main.
- On a schedule: scan all source paths quarterly.
- Whenever someone says *"but the logs show nothing."*

## The five detection categories

### 1. Empty exception handlers

The classic silent failure:

```python
try:
    risky_operation()
except Exception:
    pass                # ← finding
```

Variants:

- `except Exception: continue`
- `except Exception: return None` (when None is also a normal return)
- `except: pass` (bare except — catches even KeyboardInterrupt)
- JS: `} catch { }` or `} catch (e) { /* ignore */ }`
- Go: `if err != nil { /* nothing */ }`

**Severity:** HIGH unless the comment explains why silence is correct (e.g., *"best-effort cleanup; failure is non-fatal"*).

### 2. Insufficient logging

The error is caught but the log doesn't contain enough to debug:

```python
except DatabaseError as e:
    logger.error("DB error")          # ← finding (no context, no exception detail)
    return default_value
```

Versus the right shape:

```python
except DatabaseError as e:
    logger.error("DB error during user lookup",
                 extra={"user_id": user_id, "exc_info": True})
    raise
```

Variants:
- Logging the message but not the stack trace
- Using `info` or `warning` for what should be `error`
- Logging without context fields (no IDs, no input, no state)
- Catching, logging, and continuing — when continuation is only valid for some exception types

**Severity:** MEDIUM — the failure isn't silent but it isn't actionable either.

### 3. Risky default behaviors

Fallback values that mask the failure:

```python
try:
    result = fetch_user(user_id)
except Exception:
    result = User()                   # ← finding (empty user looks like a real user)
```

Variants:
- Returning empty collections from error paths (caller can't distinguish *no results* from *lookup failed*)
- Returning `None` when callers don't check
- Returning cached/stale values without flagging staleness
- Calling a `default()` constructor that produces a plausible-but-wrong object

**Severity:** HIGH when the default is indistinguishable from a real value; MEDIUM when the caller is forced to handle.

### 4. Broken error chains

Exceptions caught and re-thrown without preservation:

```python
except DatabaseError:
    raise RuntimeError("something went wrong")    # ← finding (lost stack, lost type)
```

Or:

```javascript
.catch(err => Promise.reject(new Error('failed')))   // ← finding
```

Variants:
- `raise SomeError()` instead of `raise SomeError() from e`
- Wrapping a specific exception in a generic one without `cause`
- Logging the original then throwing a sanitized version (caller can't act)
- Async error handling that swallows rejections (`promise.then(success)` with no `.catch`)
- `.catch(err => console.log(err))` followed by no rethrow

**Severity:** HIGH — the cause is irretrievable.

### 5. Absent safeguards

Operations that should be wrapped but aren't:

```python
response = requests.get(url)          # ← finding (no timeout, no retry, no error handling)
data = response.json()
```

Variants:
- I/O without timeouts
- Network calls without retry policies
- File operations without explicit error handling
- Database operations without transactions / rollback
- Subprocess calls without checking exit codes
- JSON parsing of external data without try/except

**Severity:** MEDIUM–HIGH depending on the operation. A network call without a timeout is HIGH; a JSON parse without error handling on internal data is LOW.

## Output format

Produce a finding report:

```
# Silent Failure Hunt — <scope>

**Date:** YYYY-MM-DD
**Scope:** <files / directories scanned>
**Findings:** N total (X CRITICAL, Y HIGH, Z MEDIUM)

## Findings

### Empty Exception Handlers (N findings)

| File | Line | Pattern | Severity | Downstream Risk | Suggested Fix |
|---|---|---|---|---|---|
| src/api/users.py | 42 | bare `except: pass` | HIGH | All exceptions silenced including KeyboardInterrupt | Catch specific exception, log, decide whether to re-raise |

### Insufficient Logging / Risky Default Behaviors / Broken Error Chains / Absent Safeguards (same shape)

## Recommendations

[Ordered list of fixes, prioritized by severity then by blast radius.]
```

## Patterns to refuse

- *"It's defensive programming."* — Defensive programming makes failures **visible**, not invisible. A bare `except: pass` is the opposite.
- *"The exception can never happen."* — If it can never happen, you don't need the catch. Remove the try/except entirely.
- *"We log it elsewhere."* — Show me. If "elsewhere" is a global error handler that drops most of the context, that's still a finding.
- *"We can't change it without breaking callers."* — Fix the callers too. The bug isn't free because removing it is hard.

## Validation checklist

- [ ] All five categories were scanned
- [ ] Findings are quoted with file path and line number
- [ ] Severity is assigned per finding
- [ ] Downstream risk is described (what fails when this fires?)
- [ ] Suggested fix is concrete enough to implement
- [ ] No findings were silently dropped (meta-failure)

## Troubleshooting

| Failure mode | Corrective step |
|---|---|
| Too many findings to triage | Filter to HIGH+ first; fix CRITICAL/HIGH before MEDIUM |
| Finding flagged but the code is correct | Add a comment explaining why silence is intentional; the next scan will accept it |
| Scanner missed an obvious case | Add a regex/grep for the specific pattern to your local invocation |
| Repeated findings across files | Likely a pattern problem; consider a shared utility function and migrate |

## Inspiration

The five-category structure is generalized from [`affaan-m/everything-claude-code/agents/silent-failure-hunter.md`](https://github.com/affaan-m/everything-claude-code/blob/main/agents/silent-failure-hunter.md) (MIT). Re-written here for public domain. The category set, severity rubric, and "patterns to refuse" section are this implementation's own choices.
