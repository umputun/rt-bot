using System;
using System.Collections.Generic;
using System.Linq;
using Bot4Bots.Github;
using Microsoft.Extensions.Logging.Debug;
using Newtonsoft.Json;
using NUnit.Framework;

namespace Bot4Bots.Tests
{
    [TestFixture]
    public class GithubGatewayTest
    {
        private string _targetUser;
        private string _targetRepo;

        [SetUp]
        public void SetUp()
        {
            _targetUser = "umputun";
            _targetRepo = "rt-bot";
        }

        [Test]
        public void GetBotsInfo_ShouldReturn_NonEmptyListOfBots()
        {
            //arrange
            var sut = CreateSut();

            //act
            var result = sut.GetSummary();

            //assert
            Assert.That(result, Is.Not.Empty);
        }

        [Test]
        public void GetBotsInfo_ShouldReturn_ListWithoutFiles()
        {
            //arrange
            var sut = CreateSut();

            //act
            var result = sut.GetSummary();

            //assert
            Assert.That(result.Select(x => x.Name), Is.Not.Contain(".gitignore"));
        }

        [Test]
        public void GetBotsInfo_ShouldReturn_ListWithoutDirectoriesDoesNotContainBotSpecFile()
        {
            //arrange
            var sut = CreateSut();

            //act
            var result = sut.GetSummary();

            //assert
            Assert.That(result.Select(x => x.Name), Is.Not.Contain("ci"));
        }

        [Test]
        public void GetBotsInfo_ShouldReturn_LastChangedByInfo()
        {
            //arrange
            var sut = CreateSut();

            //act
            var result = sut.GetSummary();

            //assert
            AssertCollection(result,
                   x => Assert.That(x.LastChangedBy, Is.Not.Null),
                   x => Assert.That(x.LastChangedBy.CommitDate, Is.GreaterThan(new DateTime(2016, 01, 01))),
                   x => Assert.That(x.LastChangedBy.User, Is.Not.Null),
                   x => Assert.That(x.LastChangedBy.User, Is.Not.Match("[<>]")));
        }

        [Test]
        public void GetBotsInfo_ShouldReturn_CreatedByInfo()
        {
            //arrange
            var sut = CreateSut();

            //act
            var result = sut.GetSummary();

            //assert
            AssertCollection(result,
                   x => Assert.That(x.CreatedBy, Is.Not.Null),
                   x => Assert.That(x.CreatedBy.CommitDate, Is.GreaterThan(new DateTime(2016, 01, 01))),
                   x => Assert.That(x.CreatedBy.User, Is.Not.Null),
                   x => Assert.That(x.CreatedBy.User, Is.Not.Match("[<>]")));
        }

        [Test]
        public void GetLastCommit_ShouldReturn_LastCommitForRepository()
        {
            //arrange
            var sut = CreateSut();

            //act
            var result = sut.GetLastCommit();

            //assert
            Assert.That(result, Is.Not.Null);
        }


        private void AssertCollection<T>(IReadOnlyCollection<T> collection, params Action<T>[] assertions)
        {
            foreach (var item in collection)
            {
                try
                {
                    foreach (var assertion in assertions)
                    {
                        assertion(item);
                    }
                }
                catch (AssertionException e)
                {
                    throw new AssertionException($"Error asserting '{JsonConvert.SerializeObject(item)}'", e);
                }
            }
        }
        
        private GithubGateway CreateSut()
        {
            return new GithubGateway(_targetUser, _targetRepo, new DebugLogger("test"));
        }
    }
}