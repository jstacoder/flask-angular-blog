var app = angular.module('app.controllers',['app.services','ngCookies']);

app.controller('HomeCtrl',HomeCtrl)
   .controller('PostsCtrl',PostsCtrl)
   .controller('PostCtrl',PostCtrl)
   .controller('AddPostCtrl',AddPostCtrl)
   .controller('NavCtrl',NavCtrl)
   .controller('LoginCtrl',LoginCtrl)
   .controller('RegisterCtrl',RegisterCtrl)
   .controller('LogoutCtrl',LogoutCtrl)
   .controller('SettingsCtrl',SettingsCtrl)
   .controller('UserPostCtrl',UserPostCtrl)
   .controller('ListGroupCtrl',ListGroupCtrl);


ListGroupCtrl.$inject = ['$scope','$element','$attrs'];
function ListGroupCtrl($scope,$element,$attrs) {
}


UserPostCtrl.$inject = ['posts'];

function UserPostCtrl(posts) {
    var self = this;

    self.posts = posts.data;
    self.collapsed = {};
    angular.forEach(self.posts,function(itm){
        self.collapsed[itm.slug] = true;
    });
}


SettingsCtrl.$inject = ['settingService','$scope','$timeout'];

function SettingsCtrl(settingService,$scope,$timeout) {
    var self = this;
    self.settings = settingService.settings.getSettings();

    setup();

    function setup() {
        self.edits = {};
        angular.forEach(
            Object.keys(
                self.settings
            ),function(itm){
                self.edits[itm] = false;
        });
    }

    function setEditMode(key) {
        self.edits[key] = !self.edits[key];
    }


    function setSetting(k,v) {
        settingService.settings.set(k,v);
        self.settings = settingService.settings.getSettings();
    }

    self.setEditMode = setEditMode;

    self.anyEdits = function(){
        var rtn = false;
        angular.forEach(self.edits,function(itm,key){
                if (itm) {
                    rtn = true;
                }
        });
        return rtn;
    };

    self.set = function(k,v){
            //setSetting(k,v);
            settingService.settings.set(k,v);
            self.settings[k] = v;
            setEditMode(k);
        //$scope.$digest ? $scope.$digest(setSetting) : $scope.$apply(setSetting);
    }
}

LoginCtrl.$inject = ['login','$cookies','sendLogin','redirect','loginError','$modal'];

function LoginCtrl(login,$cookies,sendLogin,redirect,loginError,$modal) {
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

HomeCtrl.$inject = ['$rootScope','$modal','$scope','loadUser'];

function HomeCtrl($rootScope,$modal,$scope,loadUser) {
    var self = this;
    this.test = 'hi';
    self._curr;
    self.justLoggedIn = self.justLoggedIn || false;

    $rootScope.$on('user:login',function(){
        console.log('home log 2');
        self.justLoggedIn = true;
    });

    if (self.justLoggedIn) {
        self.justLoggedIn = false;
        console.log('home log');
        $modal.open({templateUrl:"/static/partials/welcome-modal.html"}).result.then(function(){});
    }
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

PostCtrl.$inject = ['post','deletePost','$location','$window','isAuthenticated','$modal','$scope','addComment','loadUser','redirect'];

function PostCtrl(post,deletePost,$location,$window,isAuthenticated,$modal,$scope,addComment,loadUser,redirect) {
    var self = this;
    self.post = post;
    self.comments = angular.copy(post.comments || []).reverse();
    self.comment = {
        content:'',
        post_id:null,
        subject:''
    };
    self.currentUser = loadUser(5);

    self.deletePost = function(post){
        deletePost(post,'/posts');
    };

    function prePend(lst,itm){
        var newlst = [itm];
        lst.map(function(i){
            newlst.push(i);
        });
        return newlst;
    }
    function insertComment(comment) {
        if (!isAuthenticated()) {
            redirect('/login');
        }
        if (comment.parent) {
            var done = false;
            angular.forEach(self.comments,function(itm){
                if (!done) {
                    if(itm.id == comment.parent){
                        itm.children.push(comment);
                        done = true;
                    }
                }
            });
        }else{
            self.comments = prePend(self.comments,comment);
        }
    }
    self.addPostComment = function(){
        addComment(
                   {
                        subject:self.comment.subject || "reply to "+ self.post.title,
                        post_id:self.post.id,
                        parent_comment_id:null,
                        content:self.comment.content,
                        author_id:loadUser(10).id
                    }
                )
        .then(function(res){
            insertComment(res.data);
        });
    }
    self.addComment = function(post_id,cmt_id){
        var modal = $modal.open(
            {
                templateUrl:"/static/partials/comment-modal.html",
                size:'sm',
                scope:$scope.$new(),
                controller:CommentCtrl,
                controllerAs:"ctrl",
                resolve:{
                    postId:function(){
                        return post_id;
                    },
                    parentId:function(){
                        return cmt_id;
                    }
                }
            }
        );
        modal.result.then(function(res){
            console.log('success: ',res.content,res.post,res.parent);
            addComment(
                    {
                        subject:"reply",
                        post_id:res.post,
                        parent_comment_id:res.parent,
                        content:res.content,
                        author_id:loadUser(10).id
                    }
                )
                .then(function(res){
                    console.log('adding a comment',res.data);
                    insertComment(res.data);
                });
        },function(err){
            console.log('error: ',err)
        });
    };
    self.isAuthenticated = isAuthenticated;
}

CommentCtrl.$inject = ['$scope','postId','parentId'];

function CommentCtrl($scope,postId,parentId) {
    var self = this;
    self.reply = {
        parent:parentId,
        post:postId
    };
}
