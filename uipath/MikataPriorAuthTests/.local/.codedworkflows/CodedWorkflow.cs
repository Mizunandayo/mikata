using System;
using System.Collections.Generic;
using System.Data;
using UiPath.Activities.System.Jobs.Coded;
using UiPath.CodedWorkflows;
using UiPath.Core;
using UiPath.Core.Activities.Storage;
using UiPath.Orchestrator.Client.Models;
using UiPath.Testing;
using UiPath.Testing.Activities.Api.Models;
using UiPath.Testing.Activities.Models;
using UiPath.Testing.Activities.TestData;
using UiPath.Testing.Activities.TestDataQueues.Enums;
using UiPath.Testing.Enums;

namespace MikataPriorAuthTests
{
    public partial class CodedWorkflow : CodedWorkflowBase
    {
        private Lazy<global::MikataPriorAuthTests.WorkflowRunnerService> _workflowRunnerServiceLazy;
        private Lazy<ConnectionsManager> _connectionsManagerLazy;
        public CodedWorkflow()
        {
            _ = new System.Type[]
            {
                typeof(UiPath.Core.Activities.API.ISystemService),
                typeof(UiPath.Testing.API.ITestingService)
            };
            _workflowRunnerServiceLazy = new Lazy<global::MikataPriorAuthTests.WorkflowRunnerService>(() => new global::MikataPriorAuthTests.WorkflowRunnerService(this.services));
#pragma warning disable
            _connectionsManagerLazy = new Lazy<ConnectionsManager>(() => new ConnectionsManager(serviceContainer));
#pragma warning restore
        }

        protected global::MikataPriorAuthTests.WorkflowRunnerService workflows => _workflowRunnerServiceLazy.Value;
        protected ConnectionsManager connections => _connectionsManagerLazy.Value;
#pragma warning disable
        protected UiPath.Core.Activities.API.ISystemService system { get => serviceContainer.Resolve<UiPath.Core.Activities.API.ISystemService>() ; }
#pragma warning restore
#pragma warning disable
        protected UiPath.Testing.API.ITestingService testing { get => serviceContainer.Resolve<UiPath.Testing.API.ITestingService>() ; }
#pragma warning restore
    }
}