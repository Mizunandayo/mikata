using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UiPath.CodedWorkflows;
using UiPath.CodedWorkflows.Interfaces;
using UiPath.Activities.Contracts;
using MikataPriorAuthTests;

[assembly: WorkflowRunnerServiceAttribute(typeof(MikataPriorAuthTests.WorkflowRunnerService))]
namespace MikataPriorAuthTests
{
    public class WorkflowRunnerService
    {
        private readonly ICodedWorkflowServices _services;
        public WorkflowRunnerService(ICodedWorkflowServices services)
        {
            _services = services;
        }

        /// <summary>
        /// Invokes the TestCase.xaml
        /// </summary>
        /// <param name="isolated">Indicates whether to isolate executions (run them within a different process)</param>
        public void TestCase(System.Boolean isolated = false)
        {
            var result = _services.WorkflowInvocationService.RunWorkflow(@"TestCase.xaml", new Dictionary<string, object> { }, default, isolated, default, GetAssemblyName());
        }

        private string GetAssemblyName()
        {
            var assemblyProvider = _services.Container.Resolve<ILibraryAssemblyProvider>();
            return assemblyProvider.GetLibraryAssemblyName(GetType().Assembly);
        }
    }
}