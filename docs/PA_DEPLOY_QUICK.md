# PythonAnywhere Deployment - Quick Reference

## No More Stashing! 🎉

### Quick Deploy (Recommended)
```bash
git fetch origin
git reset --hard origin/main
git clean -fd
```

### Or Use the Script
```bash
bash deploy_pa.sh
```

### Manual Steps
1. SSH into PythonAnywhere
2. Run the quick deploy commands above
3. Go to Web tab → Click "Reload www.agtpricetags.com"

### That's It!
No more stashing needed. The `git reset --hard` command discards any local changes and forces your PythonAnywhere copy to match exactly what's in your GitHub repo.

### What Gets Reset?
- Any locally modified files
- Any untracked files (with `git clean -fd`)
- Everything will match your GitHub repo

### Safety
This is safe because:
1. You're working on local machine (Mac)
2. You commit and push from local
3. PythonAnywhere is just for hosting the code
4. You don't make changes directly on PythonAnywhere
