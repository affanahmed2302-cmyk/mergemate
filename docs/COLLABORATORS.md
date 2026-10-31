# Invite teammates (manual — required once)

The connected automation cannot send collaborator invites. Repo owner must do this:

1. Open https://github.com/affanahmed2302-cmyk/mergemate/settings/access
2. **Add people**
3. Invite:
   - `Monishar2809`
   - `meghapriyacs2`
4. Permission: **Write** (or Admin)
5. They must **accept the email invite**

### CLI alternative (owner machine with `gh auth login`)

```bash
gh api repos/affanahmed2302-cmyk/mergemate/collaborators/Monishar2809 -X PUT -f permission=push
gh api repos/affanahmed2302-cmyk/mergemate/collaborators/meghapriyacs2 -X PUT -f permission=push
```
