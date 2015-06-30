'use strict';

var app = angular.module('auth.app',['md5.app']);

app.constant('API_REG_URL','/api/v1/public/add');
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
app.factory('newAuthInterceptor',newAuthInterceptor);
app.factory('b64Decode',b64Decode);
app.factory('gravatarUrl',gravatarUrl);
app.factory('loadUser',loadUser);
app.factory('getAvatar',getAvatar);
app.filter('avatar',avatarFilter);
app.filter('email',emailFilter);
app.filter('username',usernameFilter);
app.service('userCache',userCache);


userCache.$inject = ['$cacheFactory'];
function userCache($cacheFactory){
    var self = this;

    self.cache = $cacheFactory('userCache');
    self.put = self.cache.put;
    self.get = self.cache.get;
    self.remove = self.cache.remove;
}

usernameFilter.$inject = ['$http','userCache'];
function usernameFilter($http) {
    return function(data){
        var rtn;
        if (!userCache.get(data)) {
            $http.get('/users/'+data+'/name').then(function(res){
                userCache.put(data,res);
            });
            rtn = '';
        }else{
            rtn = userCache.get(data);
        }
    return rtn;
    }
}

emailFilter.$inject = [];

function emailFilter() {
    return function(data,num){
        num = num ? num : 0;
        return data.emails && data.emails[num].address || '';
    }
}




sendLogin.$inject = ['$http','API_LOGIN_URL','$q','redirect'];
function sendLogin($http,API_LOGIN_URL,$q,redirect) {
    var d = $q.defer();
    return function(email,pw,success,error){
        if (email && pw) {
            console.log('sendding post');
            $http.post(API_LOGIN_URL,{email:email,password:pw}).then(function(res){
                    console.log('sent good post',res.data);
                    d.resolve(res);
                    return success(res);
               },function(err){
                    console.log('sent bad post');
                    d.reject(err);
                    return error(err);
               });
        }else{
            console.log('didnt send post');
            d.reject('errrrror');
        }
        console.log('returning from post',d.promise);
        return d.promise;
    };
}

/*appConfig.$inject = ['$httpProvider'];
function appConfig($httpProvider){
    $httpProvider.interceptors.push('newAuthInterceptor');
}
*/
appRun.$inject = ['redirect','checkAuth','$rootScope','LOGIN_URL','$location','$parse'];
function appRun(redirect,checkAuth,$rootScope,LOGIN_URL,$location,$parse){
    $rootScope.$on("$routeChangeStart",function(e,newRoute,oldRoute){
        var $route = newRoute && newRoute.$$route ? newRoute.$$route : null;
        if($route && $route.requiresAuth && !checkAuth()){
            redirect(LOGIN_URL);
        }
        if($route && $route.navOptions && $route.navOptions.show && !$parse($route.navOptions.show)($rootScope)){
        console.log($route);
            redirect('/');
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

login.$inject = ['$window','redirect','$rootScope','$modal','loadUser'];
function login($window,redirect,$rootScope,$modal,loadUser){
    return function(tkn){
        if (tkn.token) {
            tkn = tkn.token;
        }
        $window.sessionStorage.setItem('token',JSON.stringify(tkn));
        $rootScope.$broadcast('user:login',loadUser().is_public);
        $rootScope.$emit('user:login',loadUser().is_public);
        $rootScope.current  = {username:loadUser().username};
        $modal.open({templateUrl:"/static/partials/welcome-modal.html",$scope:$rootScope.$new(),size:'sm'});
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
        if(data.password && data.email){
            def.resolve($http.post(API_REG_URL,JSON.stringify(data)));
        }else{
            def.reject({reason:'insufficent data',data:data});
        }
        return def.promise;
    };
}

newAuthInterceptor.$inject = ['$q','token','redirect','$location','LOGIN_URL','loadUser','$cookies'];
function newAuthInterceptor($q,token,redirect,$location,LOGIN_URL,loadUser,$cookies){
    return {
        request:function(cfg){
            cfg.headers = cfg.headers || {};
            if(loadUser()){
                cfg.headers.Authorization = 'Bearer ' + token();
                $cookies.put('USER_AUTH',loadUser().id);
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

gravatarUrl.$inject = ['getAvatar','loadUser'];
function gravatarUrl(getAvatar,loadUser){
    var user = loadUser(5);
    if (user && user.emails.length) {
        return getAvatar(user.emails[0]);
    }
    return '';
}


getAvatar.$inject = ['md5'];
function getAvatar(md5) {
    return function avatar(email,size){
        var url = "http://www.gravatar.com/avatar/"+md5(email);
        return size ? url + '?s=' + size : url;
    };
}

avatarFilter.$inject = ['getAvatar'];
function avatarFilter(getAvatar) {
    return function avatarFilter(email,size){
        return getAvatar(email,size);
    };
}

loadUser.$inject = ['b64Decode','token','checkAuth','userCache'];
function loadUser(b64Decode,token,checkAuth,userCache){
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
                        userCache.put(user.id,user.username);
                    }
            }
            return user;
        }
        return false;
    }
}
