

module.exports = {
  pages: {
    'index': {
      entry: './src/pages/Home/main.js',
      template: './public/index.html',
      title: 'Home',
      chunks: [ 'chunk-vendors', 'chunk-common', 'index' ]
    },
    'analyze': {
      entry: './src/pages/About/main.js',
      template: './public/index.html',
      title: 'Analyze',
      chunks: [ 'chunk-vendors', 'chunk-common', 'about' ]
    },
    'data_load': {
      entry: './src/pages/Data Load/main.js',
      template: './public/data_load.html',
      title: 'Data Load',
      chunks: [ 'chunk-vendors', 'chunk-common', 'about' ]
    }
  }
}
