var app = angular.module('app.routes',['ngRoute','app.controllers']);

app.config(appRouteConfig);

appRouteConfig.$inject = ['$routeProvider','$locationProvider'];

function appRouteConfig($routeProvider,$locationProvider){
    $locationProvider.html5Mode(true);

    $routeProvider.when('/',{
        templateUrl:'static/partials/home.html',
        controller:'HomeCtrl',
        controllerAs:'ctrl',
        navOptions:{
            add:true,
            text:"Home",
        }
    })
    .when('/post/add',{
        templateUrl:'static/partials/add.html',
        controller:'AddPostCtrl',
        controllerAs:'ctrl',
        resolve:{
            posts:postResolve,
            _tags:function(tags){
                return tags;
            }
        },
        navOptions:{
            add:true,
            text:"Add Post"
        }
    })
    .when('/posts',{
        templateUrl:'static/partials/posts.html',
        controller:'PostsCtrl',
        controllerAs:'ctrl',
        resolve:{
            posts:postResolve
        },
        navOptions:{
            add:true,
            text:"Posts"
        }
    })
    .when('/post/:post_id',{
        templateUrl:'static/partials/post.html',
        controller:'PostCtrl',
        controllerAs:'ctrl',
        resolve:{
            post:function(postService,$route){
                console.log($route);
                var post = postService.get({post_id:$route.current.params.post_id});
                return post;
            },
            posts:postResolve
        },
        navOptions:{
            add:false
        }
    })
    .otherwise({
        redirectTo:'/'
    });
};

function postResolve(postService){
    return postService.query();
}
