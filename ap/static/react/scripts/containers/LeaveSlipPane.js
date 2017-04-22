import { connect } from 'react-redux'
import { postLeaveSlip, changeLeaveSlipForm } from '../actions'
import { lastLeaveslips } from '../selectors/selectors'
import LeaveSlipForm from '../components/LeaveSlipForm'

const mapStateToProps = (state) => {
  return {
    lastSlips: lastLeaveslips(state),
    form: {
      selectedEvents: state.selectedEvents,
      slipType: state.form.leaveSlip.slipType,
      ta_informed: state.form.leaveSlip.ta_informed,
      ta: state.form.leaveSlip.ta,
      comment: state.form.leaveSlip.comment,
      trainee: state.trainee,
      location: state.form.leaveSlip.location,
      hostName: state.form.leaveSlip.hostName,
      hostPhone: state.form.leaveSlip.hostPhone,
      hcNotified: state.form.leaveSlip.hcNotified,
    },
    tas: state.tas,
  }
}
const mapDispatchToProps = (dispatch) => {
  return {
    postLeaveSlip: (values) => { dispatch(postLeaveSlip(values)) },
    changeLeaveSlipForm: (values) => { dispatch(changeLeaveSlipForm(values)) }
  }
}

const LeaveSlipPane = connect(
  mapStateToProps,
  mapDispatchToProps
)(LeaveSlipForm)

export default LeaveSlipPane
