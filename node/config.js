var config = {};

config.debug = false;
config.bridgeServerPort = 9000;
config.logPath = 'bridge.log'

// Import local config if any
try {
  local_config = require('./local_config');
  Object.keys(local_config).forEach(function(key) {
    config[key] = local_config[key];
  });
} catch (e) {}

module.exports = config;
