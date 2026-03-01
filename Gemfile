source "https://rubygems.org"

# Ruby version - updated to allow 3.4.x for better compatibility
ruby ">= 3.2", "< 3.5"

# Jekyll - direct dependency (deployed via GitHub Actions, not github-pages gem)
gem "jekyll", "~> 4.4.1"

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-sitemap", "~> 1.4"
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-seo-tag", "~> 2.8"
end

# Required dependencies
gem "webrick", "~> 1.8"
gem "base64"
gem "bigdecimal"
gem "csv"
gem "http_parser.rb", "~> 0.8.1"
gem "tzinfo", ">= 1", "< 3"
gem "tzinfo-data", platforms: %i[windows jruby]

# Windows file-watching support
gem "wdm", "~> 0.1", platforms: %i[windows]
