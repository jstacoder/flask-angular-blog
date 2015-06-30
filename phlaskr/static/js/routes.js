var app = angular.module('app.routes',['ngRoute','app.controllers']);

app.config(appRouteConfig);

appRouteConfig.$inject = ['$routeProvider','$locationProvider'];

function appRouteConfig($routeProvider,$locationProvider){
    $locationProvider.html5Mode(true);

    $routeProvider.when('/',{
        templateUrl:'/static/partials/home.html',
        controller:'HomeCtrl',
        controllerAs:'ctrl',
        navOptions:{
            add:true,
            text:"Home",
            show:'true'
        }
    })
    .when('/post/add',{
        templateUrl:'/static/partials/add.html',
        controller:'AddPostCtrl',
        controllerAs:'ctrl',
        resolve:{
            posts:postUserResolve,
            _tags:function(tags){
                return tags;
            }
        },
        requiresAuth:true,
        navOptions:{
            add:true,
            text:"Add Post",
            show:'isAuthenticated&&!current.is_public'
        }
    })
    .when('/posts',{
        templateUrl:'/static/partials/posts.html',
        controller:'PostsCtrl',
        controllerAs:'ctrl',
        resolve:{
            posts:postResolve
        },
        navOptions:{
            add:true,
            text:"Posts",
            show:'true'
        }
    })
    .when('/settings',{
        templateUrl:"/static/partials/settings.html",
        controller:"SettingsCtrl",
        controllerAs:"ctrl",
        requiresAuth:true,
        navOptions:{
            add:true,
            text:"Settings",
            show:"isAuthenticated&&!current.is_public"
        }
    })
    .when('/post/:post_id',{
        templateUrl:'/static/partials/post.html',
        controller:'PostCtrl',
        controllerAs:'ctrl',
        resolve:{
            post:function(postService,$route){
                console.log($route);
                return postService.get({post_id:$route.current.params.post_id}).$promise;

            },
            posts:postResolve
        },
        navOptions:{
            add:false
        }
    })
    .when('/login',{
        templateUrl:"/static/partials/login.html",
        controller:"LoginCtrl",
        controllerAs:"ctrl",
        navOptions:{
            add:false
        }
    })
    .when('/logout',{
        controller:"LogoutCtrl",
        navOptions:{
            add:false
        },
        resolve:{
            logout:function(logout,redirect){
                logout();
                redirect('/login');
            }
        }
    })
    .when('/register',{
        templateUrl:"/static/partials/register.html",
        controller:"RegisterCtrl",
        controllerAs:"ctrl",
        navOptions:{
            add:false
        }
    })
    .when('/user/posts',{
        templateUrl:"/static/partials/user_posts.html",
        controller:"UserPostCtrl",
        controllerAs:"ctrl",
        requiresAuth:true,
        navOptions:{
            add:true,
            text:"My Posts",
            show:'isAuthenticated&&!current.is_public'
        },
        resolve:{
            posts:function(getUserPosts,loadUser){
                return getUserPosts(loadUser().id);
            }
        }
    })
    .when('/admin/:page',{
        templateUrl:function(params){
            return '/static/partials/admin/'+params.page+'.html';
        },
        controller:"AdminCtrl",
        requiresAuth:true
    })
    .when('/admin',{
        templateUrl:"/static/partials/admin/dash.html",
        controller:"AdminCtrl",
        requiresAuth:true
    })
    .otherwise({
        redirectTo:'/'
    });
};

function postResolve(postService){
    return postService.query();
}

function postUserResolve(resourceService,loadUser){
    return resourceService(loadUser().id).query();
}
