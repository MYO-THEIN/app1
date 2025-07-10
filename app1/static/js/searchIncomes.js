const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const noResults = document.querySelector(".no-results");
const tbody = document.querySelector(".table-body");

tableOutput.style.display = "none";

searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = "none";
        tbody.innerHTML = "";
    
        fetch("/incomes/search-incomes", {
            method: "POST",
            body: JSON.stringify({ "searchText": searchValue })
        })
        .then((res) => res.json())
        .then((data) => {
            appTable.style.display = "none";
            tableOutput.style.display = "block";
    
            if (data.length === 0) {
                noResults.style.display = "block";
                tableOutput.style.display = "none";
            } else {
                noResults.style.display = "none";
                data.forEach((item) => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${ item.date }</td>
                            <td>${ item.source }</td>
                            <td>${ item.description }</td>
                            <td>${ item.amount }</td>
                            <td></td>
                        </tr>
                    `;
                });
            }
        });
    } else {
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});