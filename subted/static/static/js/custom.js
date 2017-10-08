function replace_track_vtt(lang_codes){
    var t = document.querySelector(".js-player");
    var a = document.querySelector(".js-track");
    var b = a.cloneNode();

    if (lang_codes.length === 0){
        b.src = b.src.replace(window.location.origin, "").split("?")[0] + "?lang=en"
    }
    else if (lang_codes.length === 1){
        b.src = b.src.replace(window.location.origin, "").split("?")[0] + "?lang=" + lang_codes[0];
    }
    else if (lang_codes.length === 2){
        b.src = b.src.replace(window.location.origin, "").split("?")[0] + "?lang=" + lang_codes[0] + "&lang=" + lang_codes[1];
    }
    t.replaceChild(b, a)
}

function get_language_code(e) {
    var active = document.getElementsByClassName("js-list-select-languages active");
    var lang_codes = Array();
    for (i=0; i < active.length; i++){
        lang_codes.push(active[i].type)
    }
    return lang_codes
}


function update_display_transcript(lang_codes) {
    var talk_id = document.location.href.split('/')[4];
    var trans = document.getElementsByClassName("js-display-talk-transcript");
    if (lang_codes.length === 0){
        lang_codes = ['en']
    }
    if (lang_codes.length === 1){
        var url = "/api/transcript/" + talk_id + "?lang=" + lang_codes[0]
    }
    else if (lang_codes.length === 2){
        var url = "/api/transcript/" + talk_id + "?lang=" + lang_codes[0] + "&lang=" + lang_codes[1];
    }
    $.getJSON( url, function( data ) {
        var items = [];
        var transcripts_dict = data['transcripts'];
        // console.log(transcripts_dict.toString());
        if (lang_codes.length < 2) {
            for (i=0; i < transcripts_dict[lang_codes[0]].length; i++){
                items.push(transcripts_dict[lang_codes[0]][i] +"<br><br>")
            }
            }
        else if (lang_codes.length === 2) {
            var transcript_1 = transcripts_dict[lang_codes[0]];
            var transcript_2 = transcripts_dict[lang_codes[1]];
            for (i=0; i < transcript_1.length; i++){
                items.push("<p class='original-transcript'>" + transcript_1[i] +"</p><br><br>" );
                items.push("<p class='sub-transcript'>" + transcript_2[i] +"</p><br><br>" );
            }
            }
            var footer_html = document.getElementsByClassName("footer")[0].outerHTML;
            $( ".footer" ).remove();
            items.push(footer_html);
            trans[0].innerHTML = items.join("")
    });
}

function replace_download_transcripts(lang_codes) {
    var a = document.getElementsByClassName("js-download-transcript-a");
    for (i=0; i < a.length; i++) {
        var tmp = a[i].href.replace(window.location.origin, "").split("?")[0];
        if (lang_codes.length === 0) {
            a[i].href = tmp + "?lang=en"
        }
        else if (lang_codes.length === 1) {
            a[i].href = tmp + "?lang=" + lang_codes[0];
        }
        else if (lang_codes.length === 2) {
            a[i].href = tmp + "?lang=" + lang_codes[0] + "&lang=" + lang_codes[1];

        }
    }
}

function update_all() {
    var lang_codes = get_language_code();
    replace_track_vtt(lang_codes);
    replace_download_transcripts(lang_codes);
    update_display_transcript(lang_codes);
}

$(document).ready(function(){
    //active state
    $(function() {
        $('.js-list-select-languages').click(function(e) {
        e.preventDefault();
        length = document.getElementsByClassName('js-list-select-languages active').length;
        if (length < 1){
            $(this).addClass('active');
            update_all()
        }
        else if (length === 2) {
            if ($(this).hasClass("active")){
                $(this).removeClass('active');
                update_all()
            }
        }
        else{
            if ($(this).hasClass("active")){
                $(this).removeClass('active');
                update_all()
            }
            else{
                $(this).addClass('active');
                update_all()
            }
        }
        });
    });

});
