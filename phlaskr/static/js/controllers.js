var app = angular.module('app.controllers',['app.services']);

app.controller('HomeCtrl',HomeCtrl)
   .controller('PostsCtrl',PostsCtrl)
   .controller('PostCtrl',PostCtrl)
   .controller('AddPostCtrl',AddPostCtrl)
   .controller('NavCtrl',NavCtrl);

NavCtrl.$inject = ['$scope','$element','$attrs','navLinkService']

function NavCtrl($scope,$element,$attrs,navLinkService) {
    navLinkService.loadLinks();
    $scope.links = navLinkService.getLinks();
    $scope.checkLink = function(link){
        return navLinkService.checkLink(link);
    }
}

AddPostCtrl.$inject = ['posts','postService','addPost','TagService','_tags','addTag'];

function AddPostCtrl(posts,postService,addPost,TagService,_tags,addTag) {
    var self = this;
    self.posts = posts;
    self.tags = _tags;
    self.selectedTags = [];

    self.selected = function(tag){
        var rtn = false;
        angular.forEach(self.selectedTags,function(itm){
            if(tag.id === itm.id){
                rtn = true;
            }
        });
        return rtn;
    };

    self.addToSelected = function(tag){
        var contains = false,
            idx;
        angular.forEach(self.selectedTags,function(itm){
            if(itm.id === tag.id){
                contains = true;
                idx = self.selectedTags.indexOf(tag);
            }
        });
        return contains ? self.selectedTags.splice(idx,1) : self.selectedTags.push(tag) && true;
    }

    function resetPosts(){
        postService.query(function(result){
            self.posts = result;
        });
    }

    function resetTagForm() {
        self.newtag = {};
        self.newtag.text ='';
    }
    function resetForm(){
        self.newpost = {};
        self.newpost.title = '';
        self.newpost.content = '';
        self.newpost.use_jinja = false;
        self.selectedTags = [];
    }
    function submitForm() {
        var post = new postService();
        post.title = self.newpost.title;
        post.content = self.newpost.content;
        post.use_jinja = self.newpost.use_jinja;
        post.tags = self.selectedTags.map(function(itm){
            return itm.id;
        });
        addPost(post);
        resetForm();
        resetPosts();
    }
    function submitTagForm() {
        var tag = {};
        tag.name = self.newtag.name;
        tag.description = '';
        addTag(tag);
        resetTagForm();
    }
    self.onClick = submitForm;
    self.onTagClick = submitTagForm;
    resetForm();
    resetTagForm();
}

HomeCtrl.$inject = [];

function HomeCtrl() {
    var self = this;
    this.test = 'hi';
}

PostsCtrl.$inject = ['posts','deletePost'];

function PostsCtrl(posts,deletePost) {
    var self = this;
    self.posts = posts;
    self.deletePost = function(post){
        deletePost(post);
    };
}

PostCtrl.$inject = ['post','deletePost','$location','$window'];

function PostCtrl(post,deletePost,$location,$window) {
    var self = this;
    self.post = post;
    self.deletePost = function(post){
        deletePost(post);
        $location.path('/posts').replace();
    };
}
