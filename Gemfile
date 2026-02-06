source "https://rubygems.org"

# Jekyll for Netlify deployment
gem "jekyll", "~> 4.3.2"

# Required for Ruby 3.4+
gem "csv"
gem "base64"
gem "bigdecimal"

# Required plugins
gem "jekyll-feed", "~> 0.17"
gem "jekyll-sitemap", "~> 1.4"
gem "jekyll-seo-tag", "~> 2.8"

# GitHub Pages gem (optional - comment out for Netlify)
# gem "github-pages", group: :jekyll_plugins

# Optional but recommended
gem "webrick", "~> 1.8" # For local development on Ruby 3.0+

# Windows and JRuby does not include zoneinfo files
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1", :platforms => [:mingw, :x64_mingw, :mswin]

gem "http_parser.rb", "~> 0.6.0"

# Minimal Gemfile for Jekyll and Webrick to enable local build and serve
gem 'jekyll', '~> 4.3.2'
