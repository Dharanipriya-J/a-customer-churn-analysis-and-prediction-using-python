document.getElementById("predictionForm")

.addEventListener("submit",async function(e){

e.preventDefault();

const data={

gender:gender.value,

tenure:tenure.value,

monthly:monthly.value,

total:total.value,

payment_method:payment_method.value

};

const res=await fetch("/api/predict",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify(data)

});

const result=await res.json();

resultBox.innerHTML=

"<b>CHURN STATUS:</b> "+result.churn+

"<br><b>RISK LEVEL:</b> "+result.risk_level+

"<br><b>SUGGESTION:</b> "+result.suggestion;

});



document.getElementById("uploadForm")

.addEventListener("submit",async function(e){

e.preventDefault();

let file=csvFile.files[0];

let form=new FormData();

form.append("file",file);

let res=await fetch("/api/upload",{

method:"POST",

body:form

});

let data=await res.json();

tableBody.innerHTML="";

data.results.forEach(r=>{

tableBody.innerHTML+=`

<tr>

<td>${r.customer_id}</td>

<td>${r.tenure}</td>

<td>${r.monthly}</td>

<td>${r.total}</td>

<td>${r.churn}</td>

<td>${r.risk}</td>

<td>${r.suggestion}</td>

</tr>

`;

});

document.getElementById("analyticsSection").style.display="block";

loadCharts();

});


async function loadCharts(){

let res=await fetch("/api/analytics")

let data=await res.json()

new Chart(

document.getElementById("churnChart"),

{

type:'pie',

data:{

labels:['YES','NO'],

datasets:[{

data:[

data.churn_distribution.yes,

data.churn_distribution.no

]

}]

}

});

new Chart(

document.getElementById("monthlyChart"),

{

type:'bar',

data:{

labels:['Churn','Not Churn'],

datasets:[{

data:[

data.monthly_comparison.churned,

data.monthly_comparison.not_churned

]

}]

}

});

}