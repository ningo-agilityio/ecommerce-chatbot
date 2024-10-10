module.exports = {
  onPostBuild: async ({ utils }) => {
    // Custom commands after build
    console.log("Running post-build steps...");
  },
  onSuccess: async ({ utils }) => {
    console.log("Build succeeded! Running success tasks...");
    // You can add notifications, logging, etc.
  },
};