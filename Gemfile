source "https://rubygems.org"

# Ruby version - updated to allow 3.4.x for better compatibility
ruby ">= 3.2", "< 3.5"

# Core Jekyll via GitHub Pages (includes all necessary plugins)
gem "github-pages", "~> 232", group: :jekyll_plugins

# Jekyll plugins (included in github-pages, but explicit for clarity)
group :jekyll_plugins do
  gem "jekyll-remote-theme"
  gem "jekyll-sitemap"
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-paginate"
end

# Required dependencies
gem "activesupport", "~> 7.0"
gem "webrick", "~> 1.8"
gem "bigdecimal", "~> 3.1"
gem "faraday-retry", "~> 2.4"
gem "tzinfo-data", "~> 1.2024", platforms: %i[windows jruby]

# Development dependencies
group :development do
  gem "jekyll-watch", "~> 2.2"
end

# Performance (versions compatible with github-pages)
gem "sassc", "~> 2.4"  # Faster SASS compilation
