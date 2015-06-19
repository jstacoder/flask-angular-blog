var app = angular.module('app.services',['ngResource']);

app.service('postService',postService)
   .factory('posts',posts)
   .factory('addPost',addPost)
   .factory('deletePost',deletePost)
   .service('navLinkService',navLinkService)
   .factory('TagService',TagService)
   .factory('tags',tags)
   .factory('addTag',addTag)
   .factory('loginError',loginError);
   //.factory('deleteModal',deleteModal);


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
        angular.forEach(
            Object.keys(
                $route.routes
            ).filter(function(itm){
                if(itm.length===1||itm[itm.length-1]!=='/'){
                    return true;
                }
                return false;
            }),function(itm){
                console.log(itm);
                var key = itm,
                    route = $route.routes[key],
                    linkData = route.navOptions && route.navOptions.add ? {
                        href:key,
                        text:route.navOptions.text,
                        show:route.navOptions.show
                    } : {};
                console.log(route);
                console.log(linkData);
                addLink(linkData);
            });
    }
    //loadLinks();
}

postService.$inject = ['$resource'];

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
            delete:{
                url:'/api/v1/post/delete/:post_id',
                params:{post_id:"@id"},
                method:'POST'
            },
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


deletePost.$inject = ['posts','$modal','$location'];

function deletePost(posts,$modal,$location) {
    return function(post,redirectTo){
        $modal.open({
           templateUrl:"/static/partials/modal.html",
           controller:function($scope){
                $scope.title = 'Confirm Delete';
                $scope.content = 'Are you sure you want to delete this?'
           }
        }).result.then(function(res){
                       console.log(res);
                       var idx = posts.indexOf(post);
                       post.$delete({post_id:post.id});
                       posts.splice(idx,1);
                       redirectTo ? $location.path(redirectTo).replace() : false;
        });






    };
}
