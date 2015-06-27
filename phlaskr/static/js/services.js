var app = angular.module('app.services',['ngResource','app.settings']);

app.service('postService',postService)
   .factory('posts',posts)
   .factory('addPost',addPost)
   .factory('deletePost',deletePost)
   .service('navLinkService',navLinkService)
   .factory('TagService',TagService)
   .factory('tags',tags)
   .factory('addTag',addTag)
   .factory('loginError',loginError)
   .factory('addComment',addComment)
   .service('settingService',settingService)
   .constant('API_PREFIX','/api/v1')
   .factory('getUserPosts',getUserPosts)
   .factory('resourceService',resourceService)
   .factory('msgModal',msgModal);

   //.factory('deleteModal',deleteModal);
   //
msgModal.$inject = ['$modal'];

function msgModal($modal){
    return function(title,msg,addBtns){
        return $modal.open({
            templateUrl:'/static/partials/msg-modal.html',
            controller:'MsgModalCtrl',
            controllerAs:'ctrl',
            resolve:{
                title:function(){
                    return title;
                },
                msg:function(){
                    return msg;
                },
                confirm:function(){
                    return addBtns;
                }
            }
        }).result;
    };
}

getUserPosts.$inject = ['$http','API_PREFIX','$interpolate'];
function getUserPosts($http,API_PREFIX,$interpolate) {
    return function(user_id){
        return $http.get($interpolate('{{ api_prefix }}/user/{{ user_id }}/posts')({api_prefix:API_PREFIX,user_id:user_id}));
    }
}


settingService.$inject = ['setting'];

function settingService(setting) {
    var self = this;
    self.settings = setting;
}

addComment.$inject = ['$http'];
function addComment($http) {
    return function(data){
        return $http.post('/api/v1/comment/add',data
        );
    };
}

loginError.$inject = ['$rootScope','$timeout'];
function loginError($rootScope,$timeout){
    return function(){
        $rootScope.isHidden = false;
        $timeout(function(){
            $rootScope.isHidden = true;
        },2500);
    };
}

addTag.$inject = ['tags','TagService'];

function addTag(tags,TagService) {
    return function(tag){
        if (!tag.id) {
            tags.push(tag);
        }
        var tmp = new TagService({name:tag.name,description:tag.description});
        tmp.$save();
        return tag = tmp;
    }
}

tags.$inject = ['TagService'];

function tags(TagService) {
    return TagService.query();
}

TagService.$inject = ['$resource'];

function TagService($resource) {
    return $resource('/api/v1/tag/:tag_id',
                     {tag_id:"@id"},
                     {
                        save:{
                            url:"/api/v1/tag/add",
                            method:"POST"
                        }
                     }
    );
}

navLinkService.$inject = ['$route','$location','$parse','$rootScope'];

function navLinkService($route,$location,$parse,$rootScope){
    var loaded = loaded || false;

    $rootScope.$on('user:logout',function(){
        console.log('logging out');
        angular.forEach(self.getLinks(),function(itm){
            if(itm.requiresAuth){
                itm.show = false;
            }
        });
    });
    $rootScope.$on('user:login',function($event,publicUser){
        console.log(publicUser,publicUser ? 'public user logging in' : 'logging in');
        angular.forEach(self.getLinks(),function(itm){
            if(!publicUser&&itm.requiresAuth){
                itm.show = true;
            }
        });
    });
    $rootScope.$on('$routeChangeStart',function(event,newroute,oldroute){
        loadLinks();
    });
    var self = this,
        links = [];
    self.addLink = addLink;
    self.getLinks = function(){
        return getLinks();
    }
    self.loadLinks = function(){
        loadLinks();
    }
    self.checkLink = checkLink;
    function checkLink(link) {
        return (link.href || link) === $location.path();
    }
    function addLink(linkData){
        if (linkData.href) {
            links.push(linkData);
        }
    }
    function getFuncFromScope(scope,name) {
        return $parse(name)(scope);
    }
    function getLinks() {
        return links;
    }
    function loadLinks() {
        if (!loaded) {
            loaded = true
            angular.forEach(
                Object.keys(
                    $route.routes
                ).filter(function(itm){
                    if(itm.length===1||itm[itm.length-1]!=='/'){
                        return true;
                    }
                    return false;
                }),function(itm){
                    var key = itm,
                        $injector = angular.bootstrap(document.createElement('body'),['app']),                        route = $route.routes[key],
                        linkData = route.navOptions && route.navOptions.add ? {
                            href:key,
                            text:route.navOptions.text,
                            show:$injector.has(route.navOptions.show) ? $injector.get(route.navOptions.show)() :
                                $parse(route.navOptions.show)($rootScope,{show:route.navOptions.show}),
                            requiresAuth:route.requiresAuth
                        } : {};
                    addLink(linkData);
                }
            );
        }
    }
}

resourceService.$inject = ['$resource'];

function resourceService($resource) {
    return function getResource(user_id){
        return $resource('/api/v1/user/'+user_id+'/posts',{},{
            delete:{
                url:'/api/v1/post/delete/:post_id',
                params:{post_id:"@id"},
                method:'POST'
            }
        });
    }
}

postService.$inject = ['$resource','loadUser'];

function postService($resource) {
    return $resource(
        '/api/v1/post/:post_id',
        {
            post_id:"@id"
        },
        {
            query:{
                isArray:true
            },
            $delete:{
                url:'/api/v1/post/delete/:post_id',
                params:{post_id:"@id"},
                method:'POST'
            },
            userQuery:{
                url:'/api/v1/user/:user_id/posts',
                params:{user_id:loadUser().id},
                method:"POST",
            }
        }
    );
}

posts.$inject = ['postService'];

function posts(postService) {
    return postService.query();
}

addPost.$inject = ['posts'];

function addPost(posts) {
    return function(post){
        if (!post.id) {
            posts.push(post);
        }
        post.$save();
    }
}


deletePost.$inject = ['posts','$modal','$location','setting','$window','$rootScope'];

function deletePost(posts,$modal,$location,setting,$window,$rootScope) {
    return function(post,redirectTo){
        $modal.open({
           templateUrl:"/static/partials/modal.html",
           controller:function($scope){
                $scope.title = 'Confirm Delete';
                $scope.content = setting.get('DELETE_MSG');
           }
        }).result.then(function(res){
                       console.log('deleting ',res);
                       var func = $rootScope.$$phase ? function(){
                                    var idx = posts.indexOf(post);
                                    post.$delete({post_id:post.id});
                                    posts.splice(idx,1);
                                    redirectTo ? $location.path(redirectTo).replace() : false;//$window.location.reload();
                       } : function(){
                            $rootScope.$apply(function(){
                                    var idx = posts.indexOf(post);
                                    post.$delete({post_id:post.id});
                                    posts.splice(idx,1);
                                    redirectTo ? $location.path(redirectTo).replace() : false;//$window.location.reload();
                                });
                       };
                       func();
        });






    };
}
