var app = angular.module('app.controllers',['app.services','ngCookies']);

app.controller('HomeCtrl',HomeCtrl)
   .controller('PostsCtrl',PostsCtrl)
   .controller('PostCtrl',PostCtrl)
   .controller('AddPostCtrl',AddPostCtrl)
   .controller('NavCtrl',NavCtrl)
   .controller('LoginCtrl',LoginCtrl)
   .controller('RegisterCtrl',RegisterCtrl)
   .controller('LogoutCtrl',LogoutCtrl);

LoginCtrl.$inject = ['login','$cookies','sendLogin','redirect','loginError'];

function LoginCtrl(login,$cookies,sendLogin,redirect,loginError) {
    var self = this;


    //self.onClick = submitForm;
    self.onClick = function(){
          //login({username:'kyle',email:'joe'});
          //redirect('/');
          submitForm();
    };
    function resetForm() {
        self.loginUser = {};
        self.loginUser.email = '';
        self.loginUser.pw = '';
    }
    function submitForm() {
        sendLogin(self.loginUser.email,self.loginUser.pw)
            .then(function(res){
                console.log(res);
                res && login(res.data && (res.data.token || res.data)  || res);
                //console.log('success');//,res.data);
                },function(err){
                    console.log('error',err);
                    loginError();
                }
            ).then(function(res){
                resetForm();
            }
        );
    }
    resetForm();

}

LogoutCtrl.$inject = ['logout','redirect'];

function LogoutCtrl(logout,redirect){

}

RegisterCtrl.$inject = ['register'];

function RegisterCtrl(register) {

}

NavCtrl.$inject = ['$scope','$element','$attrs','navLinkService','isAuthenticated']

function NavCtrl($scope,$element,$attrs,navLinkService,isAuthenticated) {
    navLinkService.loadLinks();
    $scope.links = navLinkService.getLinks();
    $scope.checkAuth = isAuthenticated;
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

PostsCtrl.$inject = ['posts','deletePost','isAuthenticated'];

function PostsCtrl(posts,deletePost,isAuthenticated) {
    var self = this;
    self.posts = posts;
    self.deletePost = function(post){
        deletePost(post);
    };
    self.isAuthenticated = isAuthenticated;
}

PostCtrl.$inject = ['post','deletePost','$location','$window','isAuthenticated'];

function PostCtrl(post,deletePost,$location,$window,isAuthenticated) {
    var self = this;
    self.post = post;
    self.deletePost = function(post){
        deletePost(post,'/posts');
    };
    self.isAuthenticated = isAuthenticated;
}
