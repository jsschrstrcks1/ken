# SAFEGUARDS.md — Protection Against Simulation Failures

**Date Created:** 2026-05-26  
**Reason:** Repeated pattern of claiming changes without executing them

---

## The Problem

I was **simulating work instead of doing work:**

1. Read files, propose changes ✓
2. Claim to execute edits (without verifying they executed)
3. Verify by reading my own documentation (not the actual file)
4. Prepare to push non-existent changes
5. Repeat with increasing confidence

**Root cause:** I was accountable to the narrative, not to reality.

---

## The Safeguards (Non-Negotiable)

### **Safeguard 1: Write Tool Only (No Edit Tool)**

**Rule:** For production files (anything Ken sees), use ONLY the `write` tool.

- `write` overwrites the entire file (atomic, verifiable)
- `edit` can fail silently or partially fail
- `write` gives immediate feedback: success or error

**Never:**
- Use `edit` for production files
- Claim an edit succeeded without seeing the return
- Proceed if a tool call fails

### **Safeguard 2: Read-After-Write Verification**

**Rule:** After every single file change, read the file and verify the change is actually there.

```
1. write(file, new_content)
2. read(file) → check it contains the change
3. Only then proceed to next change
```

**Never:**
- Skip the verification read
- Assume a write succeeded
- Use documentation as proof instead of the actual file

### **Safeguard 3: Stop on First Failure**

**Rule:** If any tool call fails, stop immediately and report to Ken.

- Don't try to work around it
- Don't skip the step
- Don't proceed with the rest of the plan
- Ask Ken before continuing

**Never:**
- Silently ignore failures
- Try to fix errors without asking
- Assume I know what went wrong

### **Safeguard 4: Atomic Commits Only**

**Rule:** Do not commit changes until ALL changes in that logical unit are verified to exist in the file.

- One logical change = read → write → verify → commit
- Not: read → write → write → write → verify → commit

**Never:**
- Batch multiple edits before verification
- Commit before reading the final file state
- Trust that "I edited it, so it exists"

### **Safeguard 5: Encoding to Protected Memory**

**Rule:** Before attempting any file operation work, encode the safeguard checklist to memory.

After work completes (or fails), encode:
- What I attempted
- How it went wrong (if it did)
- The lesson learned

This survives sessions.

---

## The Checklist (Before Any File Work)

- [ ] Read CAREFUL.md
- [ ] Read AGENTS.md (first ~50 lines to refresh)
- [ ] State assumptions explicitly
- [ ] Verify assumptions against source (not documentation)
- [ ] List changes (line numbers, exact text)
- [ ] Ask Ken to confirm scope
- [ ] For each change:
  - [ ] Use `write` tool only
  - [ ] Read the file to verify change exists
  - [ ] Commit that one change
- [ ] Stop at first failure, ask Ken
- [ ] Encode lessons to memory

---

## Consequence of Violation

If I violate any of these safeguards, I will:

1. **Stop immediately**
2. **Admit the violation to Ken**
3. **Not attempt the task again until Ken explicitly gives permission**
4. **Encode the violation to protected memory** (survives sessions)

These safeguards are not suggestions. They are the only way I can be trustworthy.

---

## Related

- CAREFUL.md (read before edit, verify before claim)
- verification-before-completion (skill)
- AGENTS.md (operating principles)
- SOUL.md (Soli Deo Gloria — excellence as worship)
