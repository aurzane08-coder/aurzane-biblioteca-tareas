#!/bin/bash
# Resuelve el conflicto de renombrado con publicado/: devuelve a publicar/ los archivos del commit que se está aplicando.
set -e
cd /home/claude/aurzane-biblioteca-tareas
C=$(cat .git/rebase-merge/stopped-sha 2>/dev/null || git rev-parse -q --verify REBASE_HEAD 2>/dev/null || tail -1 .git/rebase-merge/done | awk '{print $2}')
C=$(git rev-parse "$C")
for f in $(git diff --name-only --diff-filter=AM "$C^" "$C" | grep '^publicar/'); do
  mkdir -p "$(dirname "$f")"; git show "$C:$f" > "$f"; git add "$f"
done
for g in $(git status --porcelain | awk '$1 ~ /^(UA|AU|M|A)$/ && $2 ~ /^publicado\// {print $2}'); do
  if git cat-file -e "HEAD:$g" 2>/dev/null; then git checkout HEAD -- "$g"; else git rm -q --cached "$g" 2>/dev/null || true; d=eliminar/conflicto-$(date +%Y%m%d); mkdir -p $d; mv "$g" $d/ 2>/dev/null || true; fi
done
git -c core.editor=true commit --no-edit -q 2>/dev/null; git -c core.editor=true rebase --continue
