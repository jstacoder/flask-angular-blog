var app = angular.module('app',['app.routes','app.directives','ui.bootstrap','auth.app','ngCookies','ui.ace']);

app.run(appRun);
/*
app.config(interceptorConfig);

interceptorConfig.$inject = ['$httpProvider'];

function interceptorConfig($httpProvider) {
    $httpProvider.interceptors.push('authInterceptor');
}

authInterceptor.$inject = ['$rootScope','$q','$window','authService','token'];
function authInterceptor($rootScope,$q,$window,authService,getToken) {
    var d = $q.defer();
    return{
        request:function(cfg){
            cfg.headers = cfg.headers || {};
            if(authService.hasData()){
                cfg.headers.Authorization = "Bearer "+token();
            }
            return cfg
        },
        response:function(res){
            console.log(res);
            if(res.status==401){
                console.log('error');
                d.reject(res);
            }else if(res.status==404){
                console.log("CATCH 404!!!");
                d.reject(res);
            }
            return res;
        }
    };
}
*/
appRun.$inject = ['$rootScope','loadUser'];
function appRun($rootScope,loadUser) {
    $rootScope.isHidden = true;
    $rootScope.isAuthenticated = loadUser() ? true : false;
    $rootScope.$on('$routeChangeSuccess',function(){
        $rootScope.isAuthenticated = loadUser() ? true : false;
    });
    var _curr;

    Object.defineProperty($rootScope,'current',{
       get: function(){
            _curr = _curr ? _curr : loadUser();
            return _curr;
        },
        set: function(val){
            _curr = loadUser();
        }
    });
}
