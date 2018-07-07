const path = require('path')

module.exports = {
    mode: "development",
    entry: "./src/main.js",
    output: {
        path: path.resolve(__dirname,'static'),
        filename: "bundle.js"
    },
    devtool: "source-map",
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /(node_modules)/,
                use:"babel-loader"
            },
            {
                test: /\.css?$/,
                exclude: /(node_modules)/,
                use: ["style-loader","css-loader"]
            }
        ]
    }
}