var app = angular.module('app.directives',[]);

app.directive('currentYear',currentYear)
   .directive('navBar',navBar);

navBar.$inject = ['navLinkService']

function navBar(navLinkService,$location) {
    return {
        restrict:"E",
        link:navBarLinkFn,
        controller:"NavCtrl",
        templateUrl:"/static/partials/navbar.html"
    };
}

function navBarLinkFn(scope,ele,attrs) {
}

function currentYear() {
    return {
        restrict:"E",
        link:currentYearLinkFn
    };
}

function currentYearLinkFn(scope,ele,attrs) {
    ele.text(new Date().getFullYear());
}
