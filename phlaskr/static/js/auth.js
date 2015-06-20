'use strict';

var app = angular.module('auth.app',['md5.app']);

app.constant('API_REG_URL','/api/v1/register');
app.constant('API_LOGIN_URL','/api/v1/login');
app.constant('LOGIN_URL','/login');
//app.config(appConfig);
app.run(appRun);
app.factory('redirect',redirect);
app.factory('checkAuth',checkAuth);
app.factory('isAuthenticated',isAuthenticated);
app.factory('login',login);
app.factory('sendLogin',sendLogin);
app.factory('logout',logout);
app.factory('token',token);
app.factory('register',register);
/*.factory('authInterceptor',authInterceptor);*/
app.factory('b64Decode',b64Decode);
app.factory('gravatarUrl',gravatarUrl);
app.factory('loadUser',loadUser);




sendLogin.$inject = ['$http','API_LOGIN_URL','$q','redirect'];
function sendLogin($http,API_LOGIN_URL,$q,redirect) {
    var d = $q.defer();
    return function(email,pw){
        if (email && pw) {
            console.log('sendding post');
            $http.post(API_LOGIN_URL,{email:email,password:pw}).then(function(res){
                    console.log('sent good post',res.data);
                    d.resolve(res);
                    redirect('/');
               },function(err){
                    console.log('sent bad post');
                    return d.reject(err);
            });
        }else{
            console.log('didnt send post');
            d.reject('errrrror');
        }
        console.log('returning from post',d.promise);
        return d.promise;
    };
}

/*appConfig.$inject = ['$httpProvider'];*/
/*function appConfig($httpProvider){
    $httpProvider.interceptors.push('authInterceptor');
}
*/
appRun.$inject = ['redirect','checkAuth','$rootScope','LOGIN_URL','$location'];
function appRun(redirect,checkAuth,$rootScope,LOGIN_URL,$location){
    $rootScope.$on("$routeChangeStart",function(e,newRoute,oldRoute){
        var $route = newRoute && newRoute.$$route ? newRoute.$$route : null;
        if($route && $route.requiresAuth && !checkAuth()){
            redirect(LOGIN_URL);
        }
        if ($location.path()==LOGIN_URL&&checkAuth()) {
            redirect('/');
        }
    });
}

redirect.$inject = ['$window','$location'];
function redirect($window,$location){
    return function(path,full){
        $location.path(path).replace();
        if (full) {
            $window.location.href = path;
        }
    };
}

checkAuth.$inject = ['isAuthenticated','$timeout'];
function checkAuth(isAuthenticated,$timeout){
    var delay;
    return function(testing){
        if(angular.isObject(testing)){
            return testing.result;
        }
        if (testing && angular.isString(testing) || angular.isNumber(testing)) {
            $timeout(function(){
                return isAuthenticated();
            },parseInt(testing)*1000);
        }
        //console.log('really checking auth');
        return isAuthenticated();
    };
}

isAuthenticated.$inject = ['$window'];
function isAuthenticated($window){
    return function(){
        return $window.sessionStorage.getItem('token') ? true : false;
    };
}

login.$inject = ['$window','redirect','$rootScope'];
function login($window,redirect,$rootScope){
    return function(tkn){
        if (tkn.token) {
            tkn = tkn.token;
        }
        $window.sessionStorage.setItem('token',JSON.stringify(tkn));
        $rootScope.$broadcast('user:login');
        $rootScope.$emit('user:login');
        redirect('/');
    };
};

logout.$inject = ['$rootScope','$window'];
function logout($rootScope,$window){
    return function(){
        console.log('logging out');
        $rootScope.$broadcast('user:logout');
        $rootScope.$emit('user:logout');
        $window.sessionStorage.removeItem('token');
    };
}

token.$inject = ['$window','$q'];
function token($window,$q){
    return function(){
        return $window.sessionStorage.getItem('token');
    };
}

register.$inject = ['$http','$q','API_REG_URL'];
function register($http,$q,API_REG_URL){
    return function(data){
        var def = $q.defer();
        if(data.username && data.password && data.email){
            def.resolve($http.post(API_REG_URL,JSON.stringify(data)));
        }else{
            def.reject(false);
        }
        return def.promise;
    };
}

authInterceptor.$inject = ['$q','token','redirect','$location','LOGIN_URL'];
function authInterceptor($q,token,redirect,$location,LOGIN_URL){
    return {
        request:function(cfg){
            cfg.headers = cfg.headers || {};
            if(token() != null){
                cfg.headers.Authorization = 'Bearer ' + token();
            }
            return cfg;
        },
        responseError:function(response){
            var def = $q.defer();
            if((response.status == 404 || response.status === 401 || response.status === 403) && $location.path() !== LOGIN_URL){
                redirect(LOGIN_URL);
            }
            return def.reject(response);
        }
    }
}

b64Decode.$inject = ['$window'];
function b64Decode($window){
    return function(s){
        var rtn = angular.isString(s) ? s.replace('-','+').replace('_','/') : s;
        switch(rtn.length % 4){
            case 0:
                break;
            case 2:
                rtn += '==';
                break;
            case 3:
                rtn += '=';
                break
            default:
                throw "illegal string";
        }
        return $window.atob(rtn);
    };
}

gravatarUrl.$inject = ['md5','loadUser'];
function gravatarUrl(md5,loadUser){
    var user = loadUser(5);
    if (user && user.emails.length) {
        return "http://www.gravatar.com/avatar/"+md5(user.emails[0]);
    }
    return '';
}

loadUser.$inject = ['b64Decode','token','checkAuth'];
function loadUser(b64Decode,token,checkAuth){
    return function(delay){
        var user = {
            name:"anonymuous",
            loggedIn:false,
            id:null
        };
        if (checkAuth(delay || 5)) {
            while (user.id == null) {
                    var encoded = token() == null ? false : token().split('.')[1];
                    if (encoded) {
                        user = JSON.parse(b64Decode(encoded));
                    }
            }
            return user;
        }
        return false;
    }
}
