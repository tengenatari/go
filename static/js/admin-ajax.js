$(document).ready(function (){
   $(document.getElementById('select-menu')).on('change', function (){
         let value = $(this).value;
      req = $.ajax({url:'/update-admin-page', table:value});
      req.done(function (data){
         let element = document.getElementById('Table')
         if (element){
            element.parentNode.removeChild(element)
            let div = document.createElement('Table');
                div.className = 'Table'
                div.id = 'Table'

               div.innerHTML = data['page']
               document.getElementById('cont').append(div)
         }
      });
   });
   $(document).on('change', '.box', function(){
      
   });
});