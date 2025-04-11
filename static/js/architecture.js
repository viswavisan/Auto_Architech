$(document).ready(function() {
    $('#menuicn').click(function() {$('.navcontainer').toggleClass("navclose")});
    $('.nav-option').click(function() {
      $('.nav-option').removeClass('selected');
      $(this).addClass('selected') ; 
      $('.page').hide();
      const pageId = $(this).attr('class').match(/option(\d+)/)[0];
      $(`#page${pageId.charAt(pageId.length - 1)}`).show();});
    $('.option1').click();
    fetch_data()

    });
  const baseurl='http://localhost:7000/'
  function logout() {
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    document.cookie = "expiry=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    window.location.href = '/login';}

  function fetch_data(){
    const data = JSON.stringify({"query": 'select'});
    Promise.all([
      fetch(`${baseurl}get_datas`, { method: "POST", headers: { 'Content-Type': 'application/json' }, body: data }).then(response => response.text()),
      fetch(`${baseurl}get_count`, { method: "POST", headers: { 'Content-Type': 'application/json' }, body: data }).then(response => response.json())])
                .then(([detailsResult, countResult]) => {create_table(detailsResult);document.getElementById('count').innerHTML = countResult;})
                .catch(error => console.log('Error:', error));
  }

  function create_table(result) {
        const table = document.getElementById('dynamic');
        table.innerHTML = "";

        const parsedResult = JSON.parse(result);
        const datas = parsedResult['data'];
        const headerRow = document.createElement('tr');
        const keys = Object.keys(datas[0]);

        keys.forEach(key => {
            const th = document.createElement('th');
            th.innerHTML = key;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        datas.forEach(data => {
            const tr = document.createElement('tr');

            keys.forEach(key => {
                const td = document.createElement('td');
                const value = data[key];

                if (typeof value === "object") {td.innerHTML = JSON.stringify(value);}
                else {td.innerHTML = value;}

                td.title = value;
                td.myparam = value;
                tr.appendChild(td);
            });

            table.appendChild(tr);
        });
    }