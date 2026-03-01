@echo off
REM One-line UX test command
npm run verify:ux && bundle exec jekyll build && bundle exec jekyll serve
