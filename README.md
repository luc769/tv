custom_spider.jar 详解（TVBox/FongMi 多爬虫合一缝合 Jar）
本质：把多个独立 csp 爬虫（XYQ、WEWA、XBPQ、Auete、XPath 等）打包编译进同一个 jar 文件，属于 CatVodTVSpider 体系。
优势：只需要加载 1 次 jar，就可以同时调用 jar 内部所有csp_xxx爬虫，不用每个源单独挂一个 jar，减少多次下载 jar 的开销。
