using System;
using System.Activities;
using UiPath.CodedWorkflows;
using UiPath.CodedWorkflows.Utils;
using System.Runtime;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Threading;
using UiPath.Robot.Activities.Api;
using UiPath.Shared.Activities;
using UiPath.Shared.Activities.Performance;
using UiPath.Testing.Activities.Performance;
using MikataPriorAuthTests;

namespace MikataPriorAuthTests
{
    [System.ComponentModel.Browsable(false)]
    public class BootloaderActivity : System.Activities.Activity
    {
        public InArgument<string> pipeName { get; set; }
        public InArgument<string> workflowPath { get; set; }
        public InArgument<Dictionary<string,object>> wfArgs { get; set; }

        public BootloaderActivity()
        {
            this.Implementation = () =>
            {
                return new BootloaderActivityChild()
                {
                    pipeName = (this.pipeName == null ? (InArgument<string>)Argument.CreateReference((Argument)new InArgument<string>(), "pipeName") : (InArgument<string>)Argument.CreateReference((Argument)this.pipeName, "pipeName")),
                    workflowPath = (this.workflowPath == null ? (InArgument<string>)Argument.CreateReference((Argument)new InArgument<string>(), "workflowPath") : (InArgument<string>)Argument.CreateReference((Argument)this.workflowPath, "workflowPath")),
                    wfArgs = (this.wfArgs == null ? (InArgument<Dictionary<string,object>>)Argument.CreateReference((Argument)new InArgument<Dictionary<string,object>>(), "wfArgs") : (InArgument<Dictionary<string,object>>)Argument.CreateReference((Argument)this.wfArgs, "wfArgs")),
                };
            };
        }
    }

    internal class BootloaderActivityChild : UiPath.CodedWorkflows.AsyncTaskCodedWorkflowActivity
    {
        public InArgument<string> pipeName { get; set; }
        public InArgument<string> workflowPath { get; set; }
        public InArgument<Dictionary<string,object>> wfArgs { get; set; }
        public System.Collections.Generic.IDictionary<string, object> newResult { get; set; }

        public BootloaderActivityChild()
        {
            DisplayName = "Bootloader";
        }

        protected override async System.Threading.Tasks.Task<Action<AsyncCodeActivityContext>> ExecuteAsync(AsyncCodeActivityContext context, System.Threading.CancellationToken cancellationToken)
        {
            var var_pipeName = pipeName.Get(context);
            var var_workflowPath = workflowPath.Get(context);
            var var_wfArgs = wfArgs.Get(context);
            var codedWorkflow = new global::MikataPriorAuthTests.Bootloader();
            CodedWorkflowHelper.Initialize(codedWorkflow, new UiPath.CodedWorkflows.Utils.CodedWorkflowsFeatureChecker(new System.Collections.Generic.List<string>() { UiPath.CodedWorkflows.Utils.CodedWorkflowsFeatures.AsyncEntrypoints }), context);
            await System.Threading.Tasks.Task.Run(() => CodedWorkflowHelper.RunWithExceptionHandlingAsync(() =>
            {
                if (codedWorkflow is IBeforeAfterRun codedWorkflowWithBeforeAfter)
                {
                    codedWorkflowWithBeforeAfter.Before(new BeforeRunContext() { RelativeFilePath = ".local\\content\\PerformanceTestingBootloaderWorkflow.cs" });
                }

                return System.Threading.Tasks.Task.CompletedTask;
            }, async () =>
            {
                await codedWorkflow.Execute(var_pipeName, var_workflowPath, var_wfArgs, cancellationToken);
                newResult = new System.Collections.Generic.Dictionary<string, object>
                {
                };
                return newResult;
            }, (exception, outArgs) =>
            {
                if (codedWorkflow is IBeforeAfterRun codedWorkflowWithBeforeAfter)
                {
                    codedWorkflowWithBeforeAfter.After(new AfterRunContext() { RelativeFilePath = ".local\\content\\PerformanceTestingBootloaderWorkflow.cs", Exception = exception });
                }

                return System.Threading.Tasks.Task.CompletedTask;
            }), cancellationToken);
            return endContext =>
            {
            };
        }
    }
}