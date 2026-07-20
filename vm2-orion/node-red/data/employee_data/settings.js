module.exports = {

    flowFile: 'flows.json',

    //credentialSecret: "a-secret-key",

    flowFilePretty: true,

    adminAuth: {
        type: "credentials",
        users: [{
            username: "admin",
            password: "$2y$08$DpP/e0Pnjnl4zrl/kJLIPe4AcjZcukPhZGTJ9.3JpGBEjXAgRH1IC",
            permissions: "*"
        }]
    },
    //httpsRefreshInterval : 12,
    //requireHttps: true,
    httpNodeAuth: [
        {
            username: "julie",
            password: "$2y$08$lAIi5EhCslZwyZoirP82fOaxkg9zn09XMTpc/ZIxTxENhGaDwklSu",
            permissions: "*"
        },
        {
            username: "florian",
            password: "$2y$08$A4bAWZUuqjenwSy3PwK2r.vnx7D.f1c8NSDC9JyVrY9ukElDHzEIO",
            permissions: "*"
        }
    ],
    //httpStaticAuth: {user:"user",pass:"$2a$08$zZWtXTja0fB1pzD4sHCMyOCMYz2Z6dNbM6tl8sJogENOMcxWV9DN."},


    uiPort: process.env.PORT || 1880,

    //uiHost: "127.0.0.1",

    //apiMaxLength: '5mb',

    //httpServerOptions: { },

    //httpAdminRoot: '/admin',
    
    // httpAdminMiddleware: function(req,res,next) {
    //    // Set the X-Frame-Options header to limit where the editor
    //    // can be embedded
    //    //res.set('X-Frame-Options', 'sameorigin');
    //    next();
    // },

    // httpAdminCookieOptions: { },

    //httpNodeRoot: '/red-nodes',

    //httpNodeCors: {
    //    origin: "*",
    //    methods: "GET,PUT,POST,DELETE"
    //},

    //httpStatic: '/home/nol/node-red-static/', //single static source

    //httpStatic: [
    //    {path: '/home/nol/pics/',    root: "/img/"},
    //    {path: '/home/nol/reports/', root: "/doc/"},
    //    {path: '/home/nol/videos/',  root: "/vid/", options: {maxAge: '1d'}}
    //],

    //httpStaticRoot: '/static/',

    //httpStaticCors: {
    //    origin: "*",
    //    methods: "GET,PUT,POST,DELETE"
    //},

    // proxyOptions: {
    //     mode: "legacy", // legacy mode is for non-strict previous proxy determination logic (node-red < v4 compatible)
    // },

    // lang: "de",

    diagnostics: {
        /** enable or disable diagnostics endpoint. Must be set to `false` to disable */
        enabled: true,
        /** enable or disable diagnostics display in the node-red editor. Must be set to `false` to disable */
        ui: true,
    },

    runtimeState: {
        /** enable or disable flows/state endpoint. Must be set to `false` to disable */
        enabled: false,
        /** show or hide runtime stop/start options in the node-red editor. Must be set to `false` to hide */
        ui: false,
    },
    telemetry: {
        // enabled: true,
        // updateNotification: true
    },
    /** Configure the logging output */
    logging: {
        console: {
            level: "info",
            /** Whether or not to include metric events in the log output */
            metrics: false,
            /** Whether or not to include audit events in the log output */
            audit: false
        }
    },

    //contextStorage: {
    //    default: {
    //        module:"localfilesystem"
    //    },
    //},

    exportGlobalContextKeys: false,

    externalModules: {
        // autoInstall: false,   /** Whether the runtime will attempt to automatically install missing modules */
        // autoInstallRetry: 30, /** Interval, in seconds, between reinstall attempts */
        // palette: {              /** Configuration for the Palette Manager */
        //     allowInstall: true, /** Enable the Palette Manager in the editor */
        //     allowUpdate: true,  /** Allow modules to be updated in the Palette Manager */
        //     allowUpload: true,  /** Allow module tgz files to be uploaded and installed */
        //     allowList: ['*'],
        //     denyList: [],
        //     allowUpdateList: ['*'],
        //     denyUpdateList: []
        // },
        // modules: {              /** Configuration for node-specified modules */
        //     allowInstall: true,
        //     allowList: [],
        //     denyList: []
        // }
    },

    //disableEditor: false,

    editorTheme: {
        //theme: "",

        //tours: false,

        palette: {
            //categories: {
            //     order: ['subflows', 'common', 'function', 'network', 'sequence', 'parser', 'storage'],
            // },
        },

        projects: {
            enabled: false,
            workflow: {
                /** Set the default projects workflow mode.
                 *  - manual - you must manually commit changes
                 *  - auto - changes are automatically committed
                 * This can be overridden per-user from the 'Git config'
                 * section of 'User Settings' within the editor
                 */
                mode: "manual"
            }
        },

        codeEditor: {
            lib: "monaco",
            options: {
                // theme: "vs",
                //fontSize: 14,
                //fontFamily: "Cascadia Code, Fira Code, Consolas, 'Courier New', monospace",
                //fontLigatures: true,
            }
        },

        markdownEditor: {
            mermaid: {
                enabled: true
            }
        },

        multiplayer: {
            enabled: false
        },
    },
    //fileWorkingDirectory: "",
    functionExternalModules: true,

    globalFunctionTimeout: 0,
    
    functionTimeout: 0,

    functionGlobalContext: {
        // os:require('os'),
    },

    //nodeMessageBufferMaxLength: 0,

    //ui: { path: "ui" },

    //debugUseColors: true,

    debugMaxLength: 1000,

    //debugStatusLength: 32,

    //execMaxBufferSize: 10000000,

    //httpRequestTimeout: 120000,

    mqttReconnectTime: 15000,

    serialReconnectTime: 15000,

    //socketReconnectTime: 10000,

    //socketTimeout: 120000,

    //tcpMsgQueueSize: 2000,

    //inboundWebSocketTimeout: 5000,


    //tlsConfigDisableLocalFiles: true,

    //webSocketNodeVerifyClient: function(info) {
    //},

    // nodeDefaults: {
    //     "debug": {
    //         "complete": true // set the debug node to show complete msg by default
    //     }
    // }
}
