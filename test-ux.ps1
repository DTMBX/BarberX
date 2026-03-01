#!/usr/bin/env pwsh
# One-line UX test command
npm run verify:ux; if ($?) { bundle exec jekyll build; if ($?) { bundle exec jekyll serve } }
