const fs = require('fs');

module.exports = function (eleventyConfig) {
  // Assets passthrough with key static files
  // 1. Specific root assets needed by templates but not in src/assets/
  eleventyConfig.addPassthroughCopy({ 'assets/css/style.css': 'assets/css/style.css' });
  eleventyConfig.addPassthroughCopy({ 'assets/css/core.css': 'assets/css/core.css' });
  eleventyConfig.addPassthroughCopy({ 'assets/css/tokens/': 'assets/css/tokens/' });
  eleventyConfig.addPassthroughCopy({ 'assets/css/components/flag-hero.css': 'assets/css/components/flag-hero.css' });
  eleventyConfig.addPassthroughCopy({ 'assets/img/flags/': 'assets/img/flags/' });
  eleventyConfig.addPassthroughCopy({ 'assets/img/logo/dark-variant-logo.svg': 'assets/img/logo/dark-variant-logo.svg' });
  eleventyConfig.addPassthroughCopy({ 'assets/img/logo/dark-variant-logo-transparent.svg': 'assets/img/logo/dark-variant-logo-transparent.svg' });
  eleventyConfig.addPassthroughCopy({ 'assets/img/logo/light-variant-logo-transparent.svg': 'assets/img/logo/light-variant-logo-transparent.svg' });
  eleventyConfig.addPassthroughCopy({ 'assets/img/brand/': 'assets/img/brand/' });
  eleventyConfig.addPassthroughCopy({ 'assets/css/components/site-header.css': 'assets/css/components/site-header.css' });
  eleventyConfig.addPassthroughCopy({ 'assets/css/components/anthem-player.css': 'assets/css/components/anthem-player.css' });
  eleventyConfig.addPassthroughCopy({ 'assets/icons/': 'assets/icons/' });
  eleventyConfig.addPassthroughCopy({ 'assets/svg/': 'assets/svg/' });

  // 2. src/assets/ — primary source for templates, components, media
  eleventyConfig.addPassthroughCopy({
    'src/assets/': 'assets/',
    'src/robots.txt': 'robots.txt',
    'src/sitemap.xml': 'sitemap.xml',
  });

  // Optimized BrowserSync config
  eleventyConfig.setBrowserSyncConfig({
    notify: false,
    ui: false,
    ghostMode: false,
    delay: 500,
  });

  // Collections for organized template authoring
  eleventyConfig.addCollection('all', (collection) =>
    collection.getFilteredByGlob('src/**/*.{md,html,njk}')
  );

  // Utility filters
  eleventyConfig.addFilter('readableDate', (dateObj) => {
    return new Date(dateObj).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  });

  // Environment variable check
  const isDev = process.env.ELEVENTY_ENV === 'development';
  const isProd = process.env.ELEVENTY_ENV === 'production';

  return {
    dir: {
      input: 'src',
      includes: '_includes',
      layouts: '_includes/layouts',
      output: '_site',
      data: '_data',
    },
    passthroughFileCopy: true,
    markdownTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk',
    templateFormats: ['md', 'njk', 'html', 'json'],
    incremental: isDev,
    quietMode: isProd,
  };
};
