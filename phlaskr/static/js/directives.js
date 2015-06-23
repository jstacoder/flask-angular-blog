var app = angular.module('app.directives',[]);

app.directive('currentYear',currentYear)
   .directive('navBar',navBar)
   .directive('listGroup',listGroup)
   .directive('listGroupItem',listGroupItem);


listGroup.$inject = [];
function listGroup() {
    return {
        restrict:"EA",
        link:listGroupLinkfn,
        transclude:true,
        controller:"ListGroupCtrl",
        template:"<div class='list-group'><ng-transclude></ng-transclude></div>"
    };
}

function listGroupLinkfn(scope,ele,attrs) {
}

listGroupItem.$inject = [];
function listGroupItem(){
    return {
        restrict:"EA",
        transclude:true,
        require:"^listGroup",
        link:listGroupItemLinkfn,
        template:"<a class='list-group-item'><ng-transclude></ng-transclude></a>"
    };
}

function listGroupItemLinkfn(scope,ele,attrs,ctrl) {
}


navBar.$inject = ['navLinkService'];

function navBar(navLinkService,$location) {
    return {
        restrict:"E",
        link:navBarLinkFn,
        controller:"NavCtrl",
        templateUrl:"/static/partials/navbar.html"
    };
}

function navBarLinkFn(scope,ele,attrs) {
    if (attrs.isAdmin) {
        scope.navclass = 'navbar-inverse';
    }else{
        scope.navclass = 'navbar-default';
    }
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
