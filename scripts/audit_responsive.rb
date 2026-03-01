require 'nokogiri'
require 'open-uri'

# Simple responsive design audit for local HTML files
SITE_DIR = File.expand_path('../_site', __dir__)
issues = []

Dir.glob(File.join(SITE_DIR, '**', '*.html')).each do |file|
  doc = Nokogiri::HTML(File.read(file))
  meta = doc.at('meta[name="viewport"]')
  unless meta && meta['content'] =~ /width=device-width/
    issues << "Missing or incorrect viewport meta in #{file}"
  end
  # Check for images without srcset
  doc.css('img').each do |img|
    unless img['srcset']
      issues << "Image missing srcset in #{file}: #{img['src']}"
    end
  end
end

if issues.any?
  puts "Responsive design issues found:"
  issues.each { |i| puts i }
else
  puts "No major responsive design issues found."
end
