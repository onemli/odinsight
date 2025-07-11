// frontend/webpack.config.js
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'workflow-builder.bundle.js',
        clean: true
    },
    mode: isProduction ? 'production' : 'development',
    
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', { targets: 'defaults' }],
                            ['@babel/preset-react', { runtime: 'automatic' }]
                        ]
                    }
                }
            },
            {
                test: /\.css$/,
                use: [
                    isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    
    plugins: [
        ...(isProduction ? [
            new MiniCssExtractPlugin({
                filename: 'workflow-builder.bundle.css'
            })
        ] : [])
    ],
    
    optimization: {
        minimize: isProduction,
        minimizer: [new TerserPlugin()]
    },
    
    resolve: {
        extensions: ['.js', '.jsx']
    }
};