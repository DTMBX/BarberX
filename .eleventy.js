module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/assets/": "assets/" });
  eleventyConfig.setBrowserSyncConfig({
    notify: false,
  });
  return {
    dir: {
      input: "src",
      includes: "_includes",
      layouts: "_includes/layouts",
      output: "_site",
    },
    passthroughFileCopy: true,
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
