        function searchDoc() {
            let search_endpoint = "https://www.hed-resources.org/en/latest/search.html?q=";
            let input = encodeURIComponent($("#searchInput").val());
            let search_args = "&check_keywords=yes&area=default#";
            window.location.href = search_endpoint + input + search_args;
        }