var app = angular.module('app.config',[]);

app.config(authUrlCfg);
app.config(addLocation);

addLocation.$inject = ['$location','$rootScope'];
function addLocation($location,$rootscope){
    $rootScope.$location = $location;
}


authUrlCfg.$inject = ['LOGIN_URL'];
function authUrlCfg(LOGIN_URL) {
    LOGIN_URL = '/api/v1/login';
}
