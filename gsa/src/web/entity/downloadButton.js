import React, { useState } from 'react'
import styled from 'styled-components'

const ClickableButton = styled.button`
  background: linear-gradient(to right, #ff6b6b, #ffc0cb);
  color: #fff;
  padding: 14px 24px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 16px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
  }
`;

const DownloadButton = (props) => {
    const [isDownload, setIsDownload] = useState(false)
    let downloadReport = () => {
        const { entities, gmp } = props;
        let options = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                reportIdArray: entities.map(entity => entity.id),
                token: gmp.settings.djangotoken,
            }),
        }
        setIsDownload(true)
        return fetch("http://172.31.119.130:8081/api/download", options)
            .then(response => {
                response.arrayBuffer().then(response => {
                    const url = window.URL.createObjectURL(new Blob([response]))
                    const link = document.createElement('a')
                    link.href = url
                    link.setAttribute('download', "summary" + '.pdf')
                    document.body.appendChild(link)
                    link.click()
                    setIsDownload(false)
                })
                    .catch(error => {
                        console.log(error);
                        setIsDownload(false)
                    })
            })
    }
    return (
        <ClickableButton onClick={() => downloadReport()}>
            {isDownload ? "Downloading...." : "Download summary report"}
        </ClickableButton>
    )
}

export default DownloadButton