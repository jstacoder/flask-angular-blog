var app = angular.module('app.settings',['ngCookies']);

app.constant('settings',{
        SITE_LOGO:"MyBlog",
        ALLOW_REGISTER:true,
        ALLOW_COMMENTS:true,
        COMMENTS_NEED_ACCOUNT:false,
        WELCOME_MSG:"Hi There {{ current.username }} welcome back!",
        DELETE_MSG:"Are You Sure You Want To Delete This?"
    }
);

app.provider('setting',setting);

setting.$inject = ['settings'];
//setting.$get.$inject = ['$parse,','$scope'];
function setting(settings) {

    var self = this;
    self.settings = {};
    return {

        $get:function($cookies,$interpolate,$parse,$rootScope){
            var svc = this;
            svc.get = getSetting;
            svc.set = setSetting;
            svc.getSettings = function(){
                return angular.extend({},settings,self.settings);
            }
            function setSetting(k,v) {
                 self.settings[k] = v;
                 $cookies.put(k,v);
             }
             function getSetting(k) {
                 //return self.settings[k] ? $parse(self.settings[k])($rootScope.$new()) : $parse(settings[k])($rootScope.$new());
                 return $interpolate(svc.getSettings()[k])($rootScope);
             }
             function setup() {
                angular.forEach(svc.getSettings(),function(v,itm){
                    if($cookies.get(itm)){
                        svc.set(itm,$cookies.get(itm));
                    }
                });
             }
             setup();
             return svc;
        }
    };
}

app.run(settingsRun);

settingsRun.$inject = ['setting','$rootScope'];

function settingsRun(setting,$rootScope) {
    $rootScope.settings = setting;
    angular.forEach(Object.keys(setting.getSettings()),function(itm){
        $rootScope[itm] = setting.get(itm);
    });
}
