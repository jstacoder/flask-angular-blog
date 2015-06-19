var app = angular.module('app.config',[]);

app.config(authUrlCfg);


authUrlCfg.$inject = ['LOGIN_URL'];
function authUrlCfg(LOGIN_URL) {
    LOGIN_URL = '/api/v1/login';
}
