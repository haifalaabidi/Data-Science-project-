let subject = document.querySelector('.ha');

const test = (subject, string) => {
    const extension = document.querySelector("#react-chrome-app");
    if (!extension) {
        const rate = document.createElement("div");
        rate.id="rate";
        rate.innerHTML = string;
        const progressBar = document.createElement("progress");
        progressBar.id="progress";
        progressBar.max=100;
        progressBar.value=50;
        
        
        const rootElement = document.createElement("div");
        rootElement.id = "react-chrome-app";
        rootElement.appendChild(rate);
        rootElement.appendChild(progressBar);
        subject.appendChild(rootElement);
        getData();
    }
};

if (subject) {

    test(subject, "Loading ...");
} else {
    // Wait for the subject element to be added to the DOM
    const observer = new MutationObserver(async function (mutationsList, observer) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList') {
                subject = document.querySelector('.ha');
                if (subject) {
                    test(subject, "Loading ...");
                    observer.disconnect();
                }
            }
        }
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

const getData = () => {
    let body = document.querySelector('.aiL')?.innerHTML;
    let subject = document.querySelector('.hP')?.innerHTML;
    let sender = document.querySelector('.go')?.innerHTML;
    let tempElement = document.querySelector('.aQH');
    let anchorElements = tempElement?.getElementsByTagName('a');

    // Extract the href attribute from each anchor element and store in an array
    let urls = [];
    if (anchorElements) {
        for (let i = 0; i < anchorElements.length; i++) {
            let href = anchorElements[i].getAttribute('href');

            urls.push(remove_html(href));
        }
    }

    sender = remove_html(sender)
    sender = sender.replace("lt;", "")
    sender = sender.replace("gt;", "")
    sender = sender.replace(/&/g, "");
    urls.push(sender);
    urls_string = urls.join("<>");
    data = {
        "subject": clean_text(subject),
        "body": clean_text(body),
        //"link_attachement": sender
    }       
    console.log(data)
    data = JSON.stringify(data)
    if (isValidJSON()){fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        body: data,
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            // Handle the response data
            document.querySelector("#rate").innerHTML = data + "%";
            const progressBar = document.querySelector('#progress');
            const progressValue = parseInt(data);
            progressBar.value = progressValue ;
            
        })
        .catch(error => {
            // Handle any errors
            console.error('Error:', error);
        });
}else{
    console.log("error")
}


}

const clean_text = (text) => {
    // Remove HTML tags using a regular expression
    text = remove_html(text)
    text = text.replace(/&nbsp;/g, "");
    // Remove special characters, line breaks, and multiple spaces
    text = text.replace(/[^\w\s]/g, "");
    text = text.replace(/[\r\n]/g, "");
    text = text.replace(/\s+/g, " ");
    text = text.replace(/\d/g, '');
    text = text.replace(/©/g, "");

    return text.trim();
};

const remove_html = (text) => {
    text = text.replace(/\\/, "");
    return text.replace(/<\/?[^>]+(>|$)/g, "");
}

const isValidJSON = (data) => {
    try {
      JSON.stringify(data);
      return true;
    } catch (error) {
      return false;
    }
  }