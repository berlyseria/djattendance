import React from 'react'
import { Alert } from 'react-bootstrap'

const TAComments = (props) => {
  return (<div>
    {
      props.comments &&
      <Alert bsStyle="warning">
        <b>TA comments:</b> {props.comments}
      </Alert>
    }
  </div>
  )
}

export default TAComments
