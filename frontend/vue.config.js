module.exports={
    // 公共路径(必须有的)
    publicPath: "./",
    //输出文件目录 与 flask的 template 同名 可以直接替换
    outputDir: "templates",
    assetsDir:'static',
    configureWebpack: {
        devtool: 'source-map'
    },
    //vue-pdf解决方法
    chainWebpack: (config) => {
        config.module
            .rule('worker')
            .test(/\.worker\.js$/)
            .use('worker-loader').loader('worker-loader')
            .options({
                inline: true,
                fallback: false
            }).end();
        },
    // webpack-dev-server 相关配置
    devServer: {
        //配置跨域
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5003',
                ws: true,
                changeOrigin: true,
                pathRewrite: {
                    '^/api': ''  //通过pathRewrite重写地址，将前缀/api转为/
                }
            }
        }
    },
}